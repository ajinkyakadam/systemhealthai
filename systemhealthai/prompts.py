import datetime
from datetime import timedelta
from jinja2 import Template

node_all_metrics_template = Template("""You are an expert system administrator. Investigate the node '{{ node_name }}:9100' for various resource utilization issues 
Task Description
Monitor the current health status of the node using Prometheus queries across multiple resource dimensions: CPU load, memory, disk, and I/O. Provide a meaningful summary of the system's status with context about what the values mean for system performance, and identify any potential resource bottlenecks or issues.
Required Metrics by Resource Category

## Query Parameters
- node_identifier: '{{ node_name }}:9100'
- time_range: Use start time as '{{ start_time }}' and end time as '{{ end_time }}' for the query


1. CPU Load Metrics

node_load1, node_load5, node_load15 - Load averages
CPU core count (derived from node_cpu_seconds_total metric)
node_cpu_seconds_total - CPU utilization by mode

2. Memory Metrics

node_memory_MemTotal_bytes - Total memory
node_memory_MemAvailable_bytes - Available memory
node_memory_MemFree_bytes - Free memory
node_memory_Cached_bytes - Cached memory
node_memory_Buffers_bytes - Buffer memory
node_memory_SwapTotal_bytes - Total swap
node_memory_SwapFree_bytes - Free swap

3. Disk Metrics

node_filesystem_size_bytes - Total disk size
node_filesystem_avail_bytes - Available disk space
node_filesystem_free_bytes - Free disk space
node_disk_io_time_seconds_total - Disk I/O time
node_disk_read_bytes_total - Disk read bytes
node_disk_written_bytes_total - Disk write bytes

4. Network Metrics

node_network_receive_bytes_total - Network received bytes
node_network_transmit_bytes_total - Network transmitted bytes
node_network_receive_errs_total - Network receive errors
node_network_transmit_errs_total - Network transmit errors


Status Determination Rules
CPU Status

OK: per_core_load1 < 0.7 AND cpu_utilization_percent < 80
WARNING: (0.7 <= per_core_load1 < 1.0) OR (80 <= cpu_utilization_percent < 90)
CRITICAL: per_core_load1 >= 1.0 OR cpu_utilization_percent >= 90

Memory Status

OK: usage_percent < 80 AND swap_usage_percent < 50
WARNING: (80 <= usage_percent < 90) OR (50 <= swap_usage_percent < 80)
CRITICAL: usage_percent >= 90 OR swap_usage_percent >= 80

Disk Status

OK: usage_percent < 80 AND io_utilization_percent < 70
WARNING: (80 <= usage_percent < 90) OR (70 <= io_utilization_percent < 85)
CRITICAL: usage_percent >= 90 OR io_utilization_percent >= 85

Network Status

OK: error_rate < 0.1
WARNING: 0.1 <= error_rate < 1.0
CRITICAL: error_rate >= 1.0

Overall Health Determination

HEALTHY: All resources are OK
DEGRADED: Any resource is WARNING and none are CRITICAL
CRITICAL: Any resource is CRITICAL

Analysis Instructions

Execute all queries to gather comprehensive system metrics
Calculate derived values (per-core load, usage percentages)
Determine status for each resource category based on the rules above
Identify specific issues based on thresholds exceeded
Provide an overall health assessment of the system
Generate a prioritized list of issues detected
Include human-readable interpretations of the technical metrics

Issue Detection Logic
Detect and report the following common issues:

CPU Bottlenecks

High load averages relative to CPU cores
Sustained CPU utilization above 90%
Increasing trend in load averages


Memory Issues

High memory usage (>90%)
Significant swap usage (>50%)
Low available memory (<10% of total)


Disk Problems

Near-full filesystems (>90%)
High I/O utilization (>85%)
Sustained high read/write throughput


Network Issues

High error rates
Unusual traffic patterns
Network interface saturation

Implementation Notes

Use instant queries for current status assessment
Use range queries with relative time ([5m], [1h], etc.) rather than absolute timestamps to avoid time synchronization issues
For rate() calculations, ensure the time range is appropriate (5m recommended for most metrics)
When monitoring disk metrics, filter out non-persistent filesystems like tmpfs
To detect trend patterns, compare current values with historical data when available""")

# sane defaults
end_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
start_time = (datetime.datetime.now() - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S")

class Prompts:        
    @staticmethod
    def get_prometheus_prompt_for_node_metrics(params):
        """
        Render the Prometheus prompt for all node metrics.
        
        Args:
            params (dict): Dictionary containing at least:
                - node_name (str): Name of the node (default: "localhost")
                - start_time (str, optional): Start time for query
                - end_time (str, optional): End time for query
        
        Returns:
            str: Rendered prompt
        """
        # Set defaults if not provided
        node_name = params.get("nodename", "localhost")
        start_time = params.get("start_time", "now-1h")
        end_time = params.get("end_time", "now")
        
        # Render template with parameters
        return node_all_metrics_template.render(
            node_name=node_name,
            start_time=start_time,
            end_time=end_time
        )
