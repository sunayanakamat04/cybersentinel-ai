"""Pydantic schemas for network flow records."""

from typing import Optional
from pydantic import BaseModel, Field


class FlowRecordSchema(BaseModel):
    """Schema representing a bidirectional network flow record."""

    flow_id: Optional[str] = Field(default=None, description="Unique flow identifier")
    timestamp: Optional[str] = Field(default=None, description="ISO-8601 flow capture timestamp")
    
    # 5-tuple addressing
    src_ip: Optional[str] = Field(default="0.0.0.0", description="Source IP address")
    src_port: int = Field(default=0, ge=0, le=65535, description="Source port (0-65535)")
    dst_ip: Optional[str] = Field(default="0.0.0.0", description="Destination IP address")
    dst_port: int = Field(default=0, ge=0, le=65535, description="Destination port (0-65535)")
    protocol: int = Field(default=6, ge=0, le=255, description="Transport protocol (e.g., 6=TCP, 17=UDP)")

    # Flow Duration & Packet Counters
    flow_duration: float = Field(default=0.0, ge=0.0, description="Flow duration in microseconds")
    total_fwd_packets: int = Field(default=0, ge=0, description="Total forward packets")
    total_bwd_packets: int = Field(default=0, ge=0, description="Total backward packets")
    total_length_fwd_packets: float = Field(default=0.0, ge=0.0, description="Total payload length of forward packets")
    total_length_bwd_packets: float = Field(default=0.0, ge=0.0, description="Total payload length of backward packets")

    # Packet Length Statistics
    fwd_packet_length_max: float = Field(default=0.0, ge=0.0)
    fwd_packet_length_min: float = Field(default=0.0, ge=0.0)
    fwd_packet_length_mean: float = Field(default=0.0, ge=0.0)
    fwd_packet_length_std: float = Field(default=0.0, ge=0.0)
    bwd_packet_length_max: float = Field(default=0.0, ge=0.0)
    bwd_packet_length_min: float = Field(default=0.0, ge=0.0)
    bwd_packet_length_mean: float = Field(default=0.0, ge=0.0)
    bwd_packet_length_std: float = Field(default=0.0, ge=0.0)

    # Rates & Throughput
    flow_bytes_per_sec: float = Field(default=0.0, description="Flow throughput in bytes/second")
    flow_packets_per_sec: float = Field(default=0.0, description="Flow throughput in packets/second")

    # Inter-Arrival Times (IAT)
    flow_iat_mean: float = Field(default=0.0, ge=0.0)
    flow_iat_std: float = Field(default=0.0, ge=0.0)
    flow_iat_max: float = Field(default=0.0, ge=0.0)
    flow_iat_min: float = Field(default=0.0, ge=0.0)
    fwd_iat_total: float = Field(default=0.0, ge=0.0)
    bwd_iat_total: float = Field(default=0.0, ge=0.0)

    # TCP Flag Counters
    fin_flag_count: int = Field(default=0, ge=0)
    syn_flag_count: int = Field(default=0, ge=0)
    rst_flag_count: int = Field(default=0, ge=0)
    psh_flag_count: int = Field(default=0, ge=0)
    ack_flag_count: int = Field(default=0, ge=0)
    urg_flag_count: int = Field(default=0, ge=0)
    fwd_psh_flags: int = Field(default=0, ge=0)
    bwd_psh_flags: int = Field(default=0, ge=0)
    fwd_urg_flags: int = Field(default=0, ge=0)
    bwd_urg_flags: int = Field(default=0, ge=0)

    # Header & Segment Metrics
    fwd_header_length: float = Field(default=0.0)
    bwd_header_length: float = Field(default=0.0)
    fwd_packets_per_sec: float = Field(default=0.0)
    bwd_packets_per_sec: float = Field(default=0.0)
    min_packet_length: float = Field(default=0.0, ge=0.0)
    max_packet_length: float = Field(default=0.0, ge=0.0)
    packet_length_mean: float = Field(default=0.0, ge=0.0)
    packet_length_std: float = Field(default=0.0, ge=0.0)
    packet_length_variance: float = Field(default=0.0, ge=0.0)
    down_up_ratio: float = Field(default=0.0, ge=0.0)
    average_packet_size: float = Field(default=0.0, ge=0.0)
    init_win_bytes_forward: int = Field(default=0, ge=0)
    init_win_bytes_backward: int = Field(default=0, ge=0)
    act_data_pkt_fwd: int = Field(default=0, ge=0)
    min_seg_size_forward: int = Field(default=0, ge=0)

    # Active & Idle Statistics
    active_mean: float = Field(default=0.0, ge=0.0)
    active_std: float = Field(default=0.0, ge=0.0)
    idle_mean: float = Field(default=0.0, ge=0.0)
    idle_std: float = Field(default=0.0, ge=0.0)

    # Ground truth (optional, for evaluation/benchmarking)
    ground_truth_label: Optional[str] = Field(default=None)
