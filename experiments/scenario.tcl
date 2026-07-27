# Reconstructed NS-2.35+nOBS experiment derived from sim20_7bmulti-cont.tcl.
# This script intentionally uses the built nOBS binary and Simulator trace-all.
# CLI: ns scenario.tcl <scenario> <seed> <attack_rate_mbps> <sim_time_s> <mitigation> ?trace_path?
# Scenarios: S0, S1, S2. Mitigation: none, rate_limit, isolation.

proc usage {} {
    puts stderr "usage: ns scenario.tcl <S0|S1|S2> <seed> <attack_rate_mbps> <sim_time_s> <none|rate_limit|isolation> ?trace_path?"
    exit 64
}

if {$argc < 5 || $argc > 6} { usage }
set scenario [lindex $argv 0]
set seed [lindex $argv 1]
set attack_rate [lindex $argv 2]
set sim_time [lindex $argv 3]
set mitigation [lindex $argv 4]
set trace_path "out.tr"
if {$argc == 6} { set trace_path [lindex $argv 5] }

if {[lsearch -exact {S0 S1 S2} $scenario] < 0} { usage }
if {![string is integer -strict $seed] || $seed <= 0} { usage }
if {![string is double -strict $attack_rate] || $attack_rate < 0.0} { usage }
if {![string is double -strict $sim_time] || $sim_time <= 0.0} { usage }
if {[lsearch -exact {none rate_limit isolation} $mitigation] < 0} { usage }
if {$scenario eq "S0" && $mitigation ne "none"} {
    puts stderr "S0 requires mitigation=none"
    exit 64
}
if {$scenario eq "S1" && $mitigation ne "none"} {
    puts stderr "S1 requires mitigation=none"
    exit 64
}
if {$scenario eq "S2" && $mitigation eq "none"} {
    puts stderr "S2 requires mitigation=rate_limit or isolation"
    exit 64
}

# Every experimental parameter is required from the versioned config runner.
# There are no silent experimental defaults in this scenario.
proc env_positive_int {name} {
    global env
    if {![info exists env($name)]} {
        puts stderr "missing required experiment parameter: $name"
        exit 64
    }
    set value $env($name)
    if {![string is integer -strict $value] || $value <= 0} {
        puts stderr "$name must be a positive integer"
        exit 64
    }
    return $value
}

proc env_positive_double {name} {
    global env
    if {![info exists env($name)]} {
        puts stderr "missing required experiment parameter: $name"
        exit 64
    }
    set value $env($name)
    if {![string is double -strict $value] || $value <= 0.0} {
        puts stderr "$name must be a positive number"
        exit 64
    }
    return $value
}

proc env_nonnegative_int {name} {
    global env
    if {![info exists env($name)]} {
        puts stderr "missing required experiment parameter: $name"
        exit 64
    }
    set value $env($name)
    if {![string is integer -strict $value] || $value < 0} {
        puts stderr "$name must be a non-negative integer"
        exit 64
    }
    return $value
}

proc env_required {name} {
    global env
    if {![info exists env($name)] || $env($name) eq ""} {
        puts stderr "missing required experiment parameter: $name"
        exit 64
    }
    return $env($name)
}

set legal_flows [env_positive_int NOBS_LEGAL_FLOWS]
set legal_packet_bytes [env_positive_int NOBS_LEGAL_PACKET_BYTES]
set attacker_count [env_positive_int NOBS_ATTACKER_COUNT]
set attacker_packet_bytes [env_positive_int NOBS_ATTACKER_PACKET_BYTES]
set legal_access_mbps [env_positive_double NOBS_LEGAL_ACCESS_MBPS]
set protected_legal_flows [env_nonnegative_int NOBS_PROTECTED_LEGAL_FLOWS]
set protected_legal_mbps [env_positive_double NOBS_PROTECTED_LEGAL_MBPS]
set attacker_access_mbps [env_positive_double NOBS_ATTACKER_ACCESS_MBPS]
set optical_rate_mbps [env_positive_double NOBS_OPTICAL_RATE_MBPS]
set optical_nodes [split [env_required NOBS_OPTICAL_NODES] ","]
set optical_node_count [llength $optical_nodes]
if {$optical_node_count == 0} { puts stderr "NOBS_OPTICAL_NODES must not be empty"; exit 64 }
set attacker_ingress [env_nonnegative_int NOBS_ATTACKER_INGRESS_NODE]
set receiver_egress [env_nonnegative_int NOBS_RECEIVER_EGRESS_NODE]
set attacker_target_receiver_index [env_nonnegative_int NOBS_ATTACKER_TARGET_RECEIVER_INDEX]
set legal_ingress_by_flow [split [env_required NOBS_LEGAL_INGRESS_BY_FLOW] ","]
if {[llength $legal_ingress_by_flow] != $legal_flows} {
    puts stderr "NOBS_LEGAL_INGRESS_BY_FLOW must contain one node per legal flow"
    exit 64
}
set optical_links [split [env_required NOBS_OPTICAL_LINKS] ";"]
set optical_routes [split [env_required NOBS_OPTICAL_ROUTES] ";"]
set legal_access_rate "${legal_access_mbps}Mb"
set access_delay_ms [env_positive_double NOBS_ACCESS_DELAY_MS]
set legal_access_delay "${access_delay_ms}ms"
set attacker_access_rate "${attacker_access_mbps}Mb"
set optical_rate "${optical_rate_mbps}Mb"
set optical_delay_ms [env_positive_double NOBS_OPTICAL_DELAY_MS]
set optical_delay "${optical_delay_ms}ms"
set receiver_access_mbps [env_positive_double NOBS_RECEIVER_ACCESS_MBPS]
set queue_length [env_positive_int NOBS_QUEUE_PACKETS]
set attack_start [env_positive_double NOBS_ATTACK_START_S]
set legal_start_stagger [env_positive_double NOBS_LEGAL_START_STAGGER_S]
set tcp_window_packets [env_positive_int NOBS_TCP_WINDOW_PACKETS]
set legal_flow_id_base [env_nonnegative_int NOBS_LEGAL_FLOW_ID_BASE]
set attacker_flow_id_base [env_nonnegative_int NOBS_ATTACKER_FLOW_ID_BASE]
set detect_delay [env_positive_double NOBS_DETECTION_DELAY_S]
set isolation_time [expr {$attack_start + $detect_delay}]
set drain_time [env_positive_double NOBS_DRAIN_TIME_S]
set finish_time [expr {$sim_time + $drain_time}]
set cir_mbps [env_positive_double NOBS_RATE_LIMIT_CIR_MBPS]
set tbf_bucket_bits [env_positive_int NOBS_TBF_BUCKET_BITS]
set tbf_queue_packets [env_nonnegative_int NOBS_TBF_QUEUE_PACKETS]
set attack_multiplier_min [env_positive_double NOBS_ATTACK_MULTIPLIER_MIN]
set attack_multiplier_max [env_positive_double NOBS_ATTACK_MULTIPLIER_MAX]
if {$attack_multiplier_max < $attack_multiplier_min} {
    puts stderr "attack multiplier max must be >= min"
    exit 64
}
# Stock TBF inherits Connector's debug binding but has no class default in
# this NS-2 tree; define it to avoid one harmless warning per instance.
TBF set debug_ 0

# Seed NS-2's default RNG before constructing any random consumers.
ns-random $seed
# The thesis varies attack intensity by roughly +/-20% between runs.  Preserve
# stable-rate CBR within each run, while deriving one reproducible run-level
# multiplier from the seed and sharing it across all eight attackers/scenarios.
set attack_rng [new RNG]
$attack_rng seed $seed
set attack_multiplier [$attack_rng uniform $attack_multiplier_min $attack_multiplier_max]
set effective_attack_rate [expr {$attack_rate * $attack_multiplier}]
set ns [new Simulator]
set settings [new OpticalDefaults]
$settings set MAX_PACKET_NUM [env_positive_int NOBS_BURST_MAX_PACKETS]
set burst_timeout_ms [env_positive_double NOBS_BURST_TIMEOUT_MS]
$settings set TIMEOUT "${burst_timeout_ms}ms"
$settings set MAX_DEST [expr {$optical_node_count + (2 * $legal_flows) + $attacker_count}]
$settings set MAX_DELAYED_BURST [env_positive_int NOBS_MAX_DELAYED_BURSTS]
$settings set MAX_FLOW_QUEUE [env_positive_int NOBS_MAX_FLOW_QUEUES]
$settings set DEBUG [env_nonnegative_int NOBS_DEBUG_LEVEL]
$settings set JET_TYPE [env_positive_int NOBS_JET_TYPE]
$settings set MAX_LAMBDA [env_positive_int NOBS_MAX_WAVELENGTHS]

$ns op_src_rting [env_nonnegative_int NOBS_SOURCE_ROUTING]
set trace_file [open $trace_path w]
$ns trace-all $trace_file

proc optical_duplex {ns n1 n2 bw delay qlen settings} {
    $ns optical-duplex-link $n1 $n2 $bw $delay OpQueue
    $ns queue-limit $n1 $n2 $qlen
    $ns queue-limit $n2 $n1 $qlen
    $settings set LINKSPEED $bw
}

# The same seven-node T optical backbone used by the upstream nOBS example:
# 0-1; 1-2-3-4; 2-6-5 (drawn as a T with ingress at 0 and 5, egress at 4).
set converter_count [env_nonnegative_int NOBS_CONVERTER_COUNT]
set optical_node_type [env_nonnegative_int NOBS_OPTICAL_NODE_TYPE]
set conversion_type [env_nonnegative_int NOBS_CONVERSION_TYPE]
set ack_dont_burst [env_nonnegative_int NOBS_ACK_DONT_BURST]
set fdl_delays [split [env_required NOBS_FDL_DELAYS_S] ","]
if {[llength $fdl_delays] == 0} { puts stderr "NOBS_FDL_DELAYS_S must not be empty"; exit 64 }
foreach i $optical_nodes {
    set n($i) [$ns OpNode]
    set src [$n($i) set src_agent_]
    eval $src optic_nodes $optical_nodes
    $src set nodetype_ $optical_node_type
    $src set conversiontype_ $conversion_type
    $src set converternumber_ $converter_count
    $src set fdlnumber_ [llength $fdl_delays]
    $src create
    eval $src fdl_size $fdl_delays
    $src set ackdontburst $ack_dont_burst

    set burst [$n($i) set burst_agent_]
    $burst burst_create
    eval $burst optic_nodes $optical_nodes
    $burst set ackdontburst $ack_dont_burst
    set classifier [$n($i) set classifier_]
    eval $classifier optic_nodes $optical_nodes
}

# Electronic node layout is derived from the upstream 40-flow nOBS example:
# legal senders 7..(7+N-1), legal receivers immediately after them, then eight
# attackers. Keeping one sender/receiver pair per TCP flow avoids the accidental
# access-link bottleneck introduced by the earlier two-endpoint reconstruction.
set legal_sender_first [expr {[lindex [lsort -integer $optical_nodes] end] + 1}]
set legal_receiver_first [expr {$legal_sender_first + $legal_flows}]
set attacker_first [expr {$legal_receiver_first + $legal_flows}]
set electronic_end [expr {$attacker_first + $attacker_count}]
for {set i $legal_sender_first} {$i < $electronic_end} {incr i} {
    set n($i) [$ns node]
    set electronic_src [$n($i) set src_agent_]
    set electronic_classifier [$n($i) set classifier_]
    eval $electronic_src optic_nodes $optical_nodes
    eval $electronic_classifier optic_nodes $optical_nodes
}

foreach encoded_link $optical_links {
    set endpoints [split $encoded_link ","]
    if {[llength $endpoints] != 2} { puts stderr "invalid optical link: $encoded_link"; exit 64 }
    optical_duplex $ns $n([lindex $endpoints 0]) $n([lindex $endpoints 1]) $optical_rate $optical_delay $queue_length $settings
}

# The first half of legal senders enters at optical node 0 and the second half
# at optical node 5, matching sim20_7bmulti-cont.tcl. Two explicitly protected
# flows retain the thesis-reported 3 Mb/s access profile; all other access links
# use the declared sensitivity parameter.
for {set k 0} {$k < $legal_flows} {incr k} {
    set src_id [expr {$legal_sender_first + $k}]
    set dst_id [expr {$legal_receiver_first + $k}]
    set ingress [lindex $legal_ingress_by_flow $k]
    set source_rate $legal_access_rate
    if {$k < $protected_legal_flows} { set source_rate "${protected_legal_mbps}Mb" }
    $ns duplex-link $n($src_id) $n($ingress) $source_rate $legal_access_delay DropTail
    $ns queue-limit $n($src_id) $n($ingress) $queue_length
    $ns queue-limit $n($ingress) $n($src_id) $queue_length
    $ns duplex-link $n($dst_id) $n($receiver_egress) "${receiver_access_mbps}Mb" $legal_access_delay DropTail
    $ns queue-limit $n($dst_id) $n($receiver_egress) $queue_length
    $ns queue-limit $n($receiver_egress) $n($dst_id) $queue_length
}
for {set i $attacker_first} {$i < $electronic_end} {incr i} {
    $ns duplex-link $n($i) $n($attacker_ingress) $attacker_access_rate $legal_access_delay DropTail
    $ns queue-limit $n($i) $n($attacker_ingress) $queue_length
    $ns queue-limit $n($attacker_ingress) $n($i) $queue_length
}

proc install_route {node_array_name src_id dst_id route} {
    upvar 1 $node_array_name nodes
    set src_agent [$nodes($src_id) set src_agent_]
    eval $src_agent install_connection $dst_id $src_id $dst_id $route
}

# Aggregate optical routes come from the experiment config.
foreach encoded_route $optical_routes {
    set fields [split $encoded_route "|"]
    if {[llength $fields] != 3} { puts stderr "invalid optical route: $encoded_route"; exit 64 }
    install_route n [lindex $fields 0] [lindex $fields 1] [lindex $fields 2]
}

# Persistent legal TCP Reno/FTP flows, one source/destination pair per flow.
# Start times are staggered over the first second as in the upstream example.
for {set k 0} {$k < $legal_flows} {incr k} {
    set src_id [expr {$legal_sender_first + $k}]
    set dst_id [expr {$legal_receiver_first + $k}]
    set ingress [lindex $legal_ingress_by_flow $k]
    set flow_id [expr {$legal_flow_id_base + $k}]
    set tcp($k) [new Agent/TCP/Reno]
    $tcp($k) set packetSize_ $legal_packet_bytes
    $tcp($k) set fid_ $flow_id
    $tcp($k) set fid2_ $flow_id
    $tcp($k) set window_ $tcp_window_packets
    $ns attach-agent $n($src_id) $tcp($k)
    $tcp($k) target [$n($src_id) set src_agent_]
    set ftp($k) [$tcp($k) attach-source FTP]

    set sink($k) [new Agent/TCPSink]
    $sink($k) set fid2_ $flow_id
    $ns attach-agent $n($dst_id) $sink($k)
    $sink($k) target [$n($dst_id) set src_agent_]
    $ns connect $tcp($k) $sink($k)

    install_route n $src_id $dst_id "$src_id $ingress $receiver_egress $dst_id"
    install_route n $dst_id $src_id "$dst_id $receiver_egress $ingress $src_id"
    $ns at [expr {$k * $legal_start_stagger}] "$ftp($k) start"
}

# Eight UDP/CBR attackers share ingress 5 and target legal receiver node 9.
# Their packets are explicitly targeted at OpSRAgent, so they enter the real nOBS
# burstifier just like TCP packets. Each attacker has its own source route.
if {$scenario ne "S0"} {
    set interval [expr {($attacker_packet_bytes * 8.0) / ($effective_attack_rate * 1000000.0)}]
    for {set k 0} {$k < $attacker_count} {incr k} {
        set src_id [expr {$attacker_first + $k}]
        set dst_id [expr {$legal_receiver_first + $attacker_target_receiver_index}]
        set flow_id [expr {$attacker_flow_id_base + $k}]
        set udp($k) [new Agent/UDP]
        $udp($k) set packetSize_ $attacker_packet_bytes
        $udp($k) set fid_ $flow_id
        $ns attach-agent $n($src_id) $udp($k)
        $udp($k) target [$n($src_id) set src_agent_]

        set attack($k) [new Application/Traffic/CBR]
        $attack($k) set packetSize_ $attacker_packet_bytes
        $attack($k) set interval_ $interval
        $attack($k) set random_ 0
        $attack($k) attach-agent $udp($k)

        set null($k) [new Agent/Null]
        $ns attach-agent $n($dst_id) $null($k)
        $null($k) target [$n($dst_id) set src_agent_]
        $ns connect $udp($k) $null($k)

        install_route n $src_id $dst_id "$src_id $attacker_ingress $receiver_egress $dst_id"
        install_route n $dst_id $src_id "$dst_id $receiver_egress $attacker_ingress $src_id"

        if {$scenario eq "S2" && $mitigation eq "rate_limit"} {
            set tbf($k) [new TBF]
            $tbf($k) set bucket_ $tbf_bucket_bits
            $tbf($k) set rate_ [expr {$cir_mbps * 1000000.0}]
            $tbf($k) set qlen_ $tbf_queue_packets
            # Install only after the declared detection delay.  qlen_=0 makes
            # stock NS-2 TBF a drop policer rather than a queueing shaper.
            $ns at $isolation_time "$udp($k) attach-tbf $tbf($k)"
        }

        if {$scenario eq "S2" && $mitigation eq "isolation"} {
            # Keep the deterministic CBR timer alive, but redirect packets to
            # a local discard agent after detection.  Stopping all generators
            # at the same instant can expose a stale partial-burst lifecycle in
            # nOBS/OpSRAgent under contention (verified SIGSEGV).  Redirecting
            # at ingress implements rate=0 isolation without touching queued
            # optical bursts, which can then drain normally.
            set isolation_sink($k) [new Agent/Null]
            $ns attach-agent $n($src_id) $isolation_sink($k)
            $ns at $isolation_time "$udp($k) target $isolation_sink($k)"
        }

        $ns at $attack_start "$attack($k) start"
        $ns at $sim_time "$attack($k) stop"
    }
}

# Stop legal sources at the measurement boundary, then retain a short drain
# interval so in-flight optical/control packets are resolved in the raw trace.
for {set k 0} {$k < $legal_flows} {incr k} {
    $ns at $sim_time "$ftp($k) stop"
}

proc finish {} {
    global ns trace_file scenario seed attack_rate sim_time mitigation trace_path
    global legal_flows legal_access_mbps optical_rate_mbps attacker_access_mbps
    global attack_multiplier effective_attack_rate drain_time
    $ns flush-trace
    close $trace_file
    puts "RUN_COMPLETE scenario=$scenario seed=$seed attack_rate_mbps=$attack_rate sim_time_s=$sim_time mitigation=$mitigation trace=$trace_path"
    puts "RUN_CONFIG legal_flows=$legal_flows legal_access_mbps=$legal_access_mbps optical_rate_mbps=$optical_rate_mbps attacker_access_mbps=$attacker_access_mbps attack_multiplier=$attack_multiplier effective_attack_rate_mbps_per_source=$effective_attack_rate drain_time_s=$drain_time"
    exit 0
}

$ns at $finish_time "finish"
$ns run
