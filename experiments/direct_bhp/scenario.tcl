# Native NS-2.35+nOBS direct-BHP control path. All experiment parameters come
# from the versioned JSON via runner.py environment variables.
# CLI: ns scenario.tcl <S0|S1|S2> <seed> <effective_rate_mbps> <duration_s> <trace> <audit> <source>
proc usage {} {
    puts stderr "usage: ns scenario.tcl <S0|S1|S2> <seed> <effective_rate_mbps> <duration_s> <trace> <audit> <source>"
    exit 64
}
proc required {name} {
    global env
    if {![info exists env($name)] || $env($name) eq ""} {
        puts stderr "missing required experiment parameter: $name"
        exit 64
    }
    return $env($name)
}
proc positive {name} {
    set value [required $name]
    if {![string is double -strict $value] || $value <= 0} {
        puts stderr "invalid positive experiment parameter: $name"
        exit 64
    }
    return $value
}
proc nonnegative {name} {
    set value [required $name]
    if {![string is double -strict $value] || $value < 0} {
        puts stderr "invalid nonnegative experiment parameter: $name"
        exit 64
    }
    return $value
}
proc positive_int {name} {
    set value [required $name]
    if {![string is integer -strict $value] || $value <= 0} {
        puts stderr "invalid positive integer experiment parameter: $name"
        exit 64
    }
    return $value
}
proc nonnegative_int {name} {
    set value [required $name]
    if {![string is integer -strict $value] || $value < 0} {
        puts stderr "invalid nonnegative integer experiment parameter: $name"
        exit 64
    }
    return $value
}
if {$argc != 7} { usage }
set scenario [lindex $argv 0]
set seed [lindex $argv 1]
set effective_rate [lindex $argv 2]
set duration [lindex $argv 3]
set trace_path [lindex $argv 4]
set audit_path [lindex $argv 5]
set source_path [lindex $argv 6]
if {[lsearch -exact {S0 S1 S2} $scenario] < 0 ||
    ![string is integer -strict $seed] || $seed <= 0 ||
    ![string is double -strict $effective_rate] || $effective_rate <= 0 ||
    ![string is double -strict $duration] || $duration <= 0} { usage }

set attack_enabled [nonnegative_int NOBS_ATTACK_ENABLED]
if {$attack_enabled > 1} { usage }
if {($scenario eq "S0" && $attack_enabled != 0) ||
    ($scenario ne "S0" && $attack_enabled != 1)} {
    puts stderr "scenario/attack semantics mismatch"
    exit 64
}
set optical_nodes [split [required NOBS_OPTICAL_NODES] ,]
set optical_links [split [required NOBS_OPTICAL_LINKS] {;}]
set optical_routes [split [required NOBS_OPTICAL_ROUTES] {;}]
set legal_senders [split [required NOBS_LEGAL_SENDERS] ,]
set legal_receivers [split [required NOBS_LEGAL_RECEIVERS] ,]
set legal_ingresses [split [required NOBS_LEGAL_INGRESSES] ,]
set legal_flows [positive_int NOBS_LEGAL_FLOW_COUNT]
if {[llength $legal_senders] != $legal_flows || [llength $legal_receivers] != $legal_flows || [llength $legal_ingresses] != $legal_flows} {
    puts stderr "legal endpoint/ingress cardinality mismatch"
    exit 64
}
set attacker_ingress [nonnegative_int NOBS_ATTACKER_INGRESS]
set receiver_egress [nonnegative_int NOBS_RECEIVER_EGRESS]
set legal_packet_bytes [positive_int NOBS_LEGAL_PACKET_BYTES]
set legal_access_mbps [positive NOBS_LEGAL_ACCESS_MBPS]
set tcp_window [positive_int NOBS_TCP_WINDOW_PACKETS]
set start_stagger [nonnegative NOBS_LEGAL_START_STAGGER_S]
set legal_flow_base [nonnegative_int NOBS_LEGAL_FLOW_ID_BASE]
set attacker_count [positive_int NOBS_ATTACKER_COUNT]
set attacker_start [nonnegative NOBS_ATTACK_START_S]
set attacker_stop [positive NOBS_ATTACK_STOP_S]
set claimed_bytes [positive_int NOBS_ATTACKER_PACKET_BYTES]
set claimed_packet_count [positive_int NOBS_BHP_CLAIMED_PACKET_COUNT]
set route_class [nonnegative_int NOBS_BHP_ROUTE_CLASS]
set optical_rate [positive NOBS_OPTICAL_RATE_MBPS]
set optical_delay [positive NOBS_OPTICAL_DELAY_MS]
set receiver_access [positive NOBS_RECEIVER_ACCESS_MBPS]
set access_delay [positive NOBS_ACCESS_DELAY_MS]
set queue_packets [positive_int NOBS_QUEUE_PACKETS]
set node_type [nonnegative_int NOBS_NODE_TYPE]
set conversion_type [nonnegative_int NOBS_CONVERSION_TYPE]
set converter_count [nonnegative_int NOBS_CONVERTER_COUNT]
set max_lambda [positive_int NOBS_MAX_WAVELENGTHS]
set burst_max_packets [positive_int NOBS_BURST_MAX_PACKETS]
set burst_timeout [positive NOBS_BURST_TIMEOUT_MS]
set max_delayed [positive_int NOBS_MAX_DELAYED_BURSTS]
set max_flow_queues [positive_int NOBS_MAX_FLOW_QUEUES]
set jet_type [nonnegative_int NOBS_JET_TYPE]
set source_routing [nonnegative_int NOBS_SOURCE_ROUTING]
set ack_dont_burst [nonnegative_int NOBS_ACK_DONT_BURST]
set fdl_delays [split [required NOBS_FDL_DELAYS_S] ,]
set event_capacity [positive NOBS_GUARD_EVENT_CAPACITY]
set event_rate [nonnegative NOBS_GUARD_EVENT_RATE]
set reservation_capacity [positive NOBS_GUARD_RESERVATION_CAPACITY]
set reservation_rate [nonnegative NOBS_GUARD_RESERVATION_RATE]
set violations [positive_int NOBS_GUARD_VIOLATIONS]
set hold_down [positive NOBS_GUARD_HOLD_DOWN_S]
set limited_release [positive NOBS_GUARD_LIMITED_RELEASE_S]

ns-random $seed
set ns [new Simulator]
set settings [new OpticalDefaults]
$settings set MAX_PACKET_NUM $burst_max_packets
$settings set TIMEOUT "${burst_timeout}ms"
set max_dest [lindex $optical_nodes end]
foreach endpoint [concat $legal_senders $legal_receivers [list $attacker_ingress $receiver_egress]] {
    if {$endpoint > $max_dest} { set max_dest $endpoint }
}
$settings set MAX_DEST [expr {$max_dest + 1}]
$settings set MAX_DELAYED_BURST $max_delayed
$settings set MAX_FLOW_QUEUE $max_flow_queues
$settings set DEBUG 0
$settings set JET_TYPE $jet_type
$settings set MAX_LAMBDA $max_lambda
$ns op_src_rting $source_routing
set trace_file [open $trace_path w]
$ns trace-all $trace_file
# Ensure both audit artifacts exist even in S0, where no producer is created.
set source_file [open $source_path w]
close $source_file

proc optical_duplex {ns left right rate delay queue settings} {
    $ns optical-duplex-link $left $right "${rate}Mb" "${delay}ms" OpQueue
    $ns queue-limit $left $right $queue
    $ns queue-limit $right $left $queue
    $settings set LINKSPEED "${rate}Mb"
}
proc install_route {nodes_name source destination path} {
    upvar 1 $nodes_name nodes
    set agent [$nodes($source) set src_agent_]
    eval $agent install_connection $destination $source $destination $path
}

foreach id $optical_nodes {
    set n($id) [$ns OpNode]
    set source_agent [$n($id) set src_agent_]
    eval $source_agent optic_nodes $optical_nodes
    $source_agent set nodetype_ $node_type
    $source_agent set conversiontype_ $conversion_type
    $source_agent set converternumber_ $converter_count
    $source_agent set fdlnumber_ [llength $fdl_delays]
    $source_agent create
    eval $source_agent fdl_size $fdl_delays
    $source_agent set ackdontburst $ack_dont_burst
    # Every optical source-route agent shares the append-only audit path so
    # a direct control can emit its terminal OUTCOME at the actual egress.
    # Only the trusted ingress enables the guard below; other nodes merely
    # obtain a writer for lifecycle evidence.
    $source_agent bhp-guard-log $audit_path
    set burst_agent [$n($id) set burst_agent_]
    $burst_agent burst_create
    eval $burst_agent optic_nodes $optical_nodes
    $burst_agent set ackdontburst $ack_dont_burst
    eval [$n($id) set classifier_] optic_nodes $optical_nodes
}
foreach encoded $optical_links {
    set edge [split $encoded ,]
    if {[llength $edge] != 2} { puts stderr "invalid optical link"; exit 64 }
    optical_duplex $ns $n([lindex $edge 0]) $n([lindex $edge 1]) $optical_rate $optical_delay $queue_packets $settings
}
foreach encoded $optical_routes {
    set fields [split $encoded {|}]
    if {[llength $fields] != 3} { puts stderr "invalid optical route"; exit 64 }
    install_route n [lindex $fields 0] [lindex $fields 1] [lindex $fields 2]
}

set endpoints [concat $legal_senders $legal_receivers]
foreach id $endpoints {
    set n($id) [$ns node]
    eval [$n($id) set src_agent_] optic_nodes $optical_nodes
    eval [$n($id) set classifier_] optic_nodes $optical_nodes
}
for {set k 0} {$k < $legal_flows} {incr k} {
    set sender [lindex $legal_senders $k]
    set receiver [lindex $legal_receivers $k]
    set ingress [lindex $legal_ingresses $k]
    $ns duplex-link $n($sender) $n($ingress) "${legal_access_mbps}Mb" "${access_delay}ms" DropTail
    $ns duplex-link $n($receiver) $n($receiver_egress) "${receiver_access}Mb" "${access_delay}ms" DropTail
    foreach pair [list [list $sender $ingress] [list $ingress $sender] [list $receiver $receiver_egress] [list $receiver_egress $receiver]] {
        $ns queue-limit $n([lindex $pair 0]) $n([lindex $pair 1]) $queue_packets
    }
    set flow [expr {$legal_flow_base + $k}]
    set tcp($k) [new Agent/TCP/Reno]
    $tcp($k) set packetSize_ $legal_packet_bytes
    $tcp($k) set fid_ $flow
    $tcp($k) set fid2_ $flow
    $tcp($k) set window_ $tcp_window
    $ns attach-agent $n($sender) $tcp($k)
    $tcp($k) target [$n($sender) set src_agent_]
    set ftp($k) [$tcp($k) attach-source FTP]
    set sink($k) [new Agent/TCPSink]
    $sink($k) set fid2_ $flow
    $ns attach-agent $n($receiver) $sink($k)
    $sink($k) target [$n($receiver) set src_agent_]
    $ns connect $tcp($k) $sink($k)
    install_route n $sender $receiver "$sender $ingress $receiver_egress $receiver"
    install_route n $receiver $sender "$receiver $receiver_egress $ingress $sender"
    $ns at [expr {$k * $start_stagger}] "$ftp($k) start"
}

set guard [$n($attacker_ingress) set src_agent_]
$guard bhp-guard-ingress $attacker_ingress
$guard bhp-guard-profile $event_capacity $event_rate $reservation_capacity $reservation_rate $violations $hold_down $limited_release
$guard bhp-guard-log $audit_path
$guard bhp-guard-enable 1

Agent/BHPFlood set destination_ 0
Agent/BHPFlood set claimedBurstBytes_ 0
Agent/BHPFlood set claimedPacketCount_ $claimed_packet_count
Agent/BHPFlood set interval_ 0
Agent/BHPFlood set trustedAttachment_ -1
Agent/BHPFlood set routeClass_ -1
if {$attack_enabled} {
    set interval [expr {($claimed_bytes * 8.0) / ($effective_rate * 1000000.0)}]
    for {set k 0} {$k < $attacker_count} {incr k} {
        set bhp($k) [new Agent/BHPFlood]
        $bhp($k) set destination_ $receiver_egress
        $bhp($k) set claimedBurstBytes_ $claimed_bytes
        $bhp($k) set claimedPacketCount_ $claimed_packet_count
        $bhp($k) set interval_ $interval
        $bhp($k) set trustedAttachment_ $attacker_ingress
        $bhp($k) set routeClass_ $route_class
        $ns attach-agent $n($attacker_ingress) $bhp($k)
        $bhp($k) target $guard
        $bhp($k) audit-log $source_path
        $ns at $attacker_start "$bhp($k) start"
        $ns at $attacker_stop "$bhp($k) stop"
    }
}
proc finish {} {
    global ns trace_file scenario seed effective_rate duration trace_path guard
    $ns flush-trace
    close $trace_file
    puts "RUN_COMPLETE scenario=$scenario seed=$seed effective_rate_mbps=$effective_rate duration_s=$duration trace=$trace_path"
    puts "BHP_COUNTERS [$guard bhp-guard-counters]"
    exit 0
}
$ns at $duration "finish"
$ns run
