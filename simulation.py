# fichier top  = liens entre les noeuds avec le debit et le delai en Gb -> Mb diminution d'un facteur 1000
# fichier traf = traffic entre les noeuds avec la taille en Mb -> octets diminution d'un facteur 1000000
import sys
import random
import math
import numpy
#import matplotlib.pyplot as plt

duree_simulation        = float(900.0)
duree_simulation_record = int(duree_simulation) * 3
a                       = float(1.1)


# topology    = fichier de la topologie contenant les liens
# fichier_tcl = fichier TCL sur lequel on ecrit
# queue_limit =  taille limite des files d'attente
def create_topology(topology, fichier_tcl, queue_limit) :

    nodes = []

    # parcours du fichier topo.top
    for line in topology :
        stripped = line.strip()

        if not stripped :
            continue
        else :
            temp = stripped.split(' ')

            src         = temp[0]
            dest        = temp[1]
            bandwidth   = temp[2]
            delay       = temp[3]

            # creation des noeuds
            if src not in nodes :
                fichier_tcl.write("set n(%s) [$ns node]\n" %(src))
                nodes.append(src)
            if dest not in nodes :
                fichier_tcl.write("set n(%s) [$ns node]\n" %(dest))
                nodes.append(dest)

            fichier_tcl.write("$ns duplex-link $n(%s) $n(%s) %sMb %sms DropTail\n" %(src, dest, bandwidth, delay))
            fichier_tcl.write("$ns queue-limit $n(%s) $n(%s) %s\n" %(src, dest, queue_limit)) # file d'attente
            # ecriture dans le fichier loss.tr
            fichier_tcl.write("set monitor_queue(%s,%s) [$ns monitor-queue $n(%s) $n(%s) queue(%s,%s) 1]\n" %(src, dest, src, dest, src, dest))
            fichier_tcl.write("set monitor_queue(%s,%s) [$ns monitor-queue $n(%s) $n(%s) queue(%s,%s) 1]\n" %(dest, src, dest, src, dest, src))
            fichier_tcl.write("$ns at %s \"record %s %s\"\n" %(duree_simulation_record, src, dest))
    return

# traffic             = fichier contenant le trafic entre les liens
# fichier_tcl         = fichier TCL sur lequel on ecrit
# simulation_duration = duree simulee (en secondes)
# burst_time          = esperance de la duree des periodes de ON
# idle_time           = esperance de la duree des periodes de OFF
# periode_on          = periode ON
# taille_packet       = taille de paquets
# shape               = courbure de Pareto
def create_traffic(traffic, fichier_tcl, simulation_duration, burst_time, idle_time, shape, periode_on, taille_packet):
    
    # mise en place des dates de demarrages et d'arret
    start_date = math.floor(simulation_duration * 0.05)
    end_date = math.floor(simulation_duration * 1.05)
    
    # nb de flux totaux et temoins generes
    flows       = 0
    flows_tcp   = 0
    retard      = 0.8

    # parcours du fichier traff.traf
    for line in traffic :
        stripped = line.strip()

        if stripped :
            temp = stripped.split(' ')

            src         = temp[0]
            dest        = temp[1]
            volume      = int(temp[2])

            # calcul des volumes Pareto et TCP a envoyer
            pareto_volume   = int(volume * periode_on)
            tcp_volume      = int(volume * (1.0 - periode_on))

            # calcul du debit
            rate = (pareto_volume / simulation_duration)* 2

            # creation et connection des agents UDP
            fichier_tcl.write("set udp_sender(%s.%s) [new Agent/UDP]\n" %(src, dest))
            fichier_tcl.write("set udp_receiver(%s.%s) [new Agent/Null]\n" %(src, dest))
            fichier_tcl.write("$ns attach-agent $n(%s) $udp_sender(%s.%s)\n" %(src, src, dest))
            fichier_tcl.write("$ns attach-agent $n(%s) $udp_receiver(%s.%s)\n" %(dest, src, dest))
            fichier_tcl.write("$ns connect $udp_sender(%s.%s) $udp_receiver(%s.%s)\n" %(src, dest, src, dest))

            # application Pareto attache aux agents UDP
            fichier_tcl.write("set pareto_app(%s.%s) [new Application/Traffic/Pareto]\n" %(src, dest))
            fichier_tcl.write("$pareto_app(%s.%s) set burst_time_ %ss\n" %(src, dest, burst_time))
            fichier_tcl.write("$pareto_app(%s.%s) set idle_time_ %ss\n" %(src, dest, idle_time))
            # on multiplie par huit pour obtenir des octets
            fichier_tcl.write("$pareto_app(%s.%s) set rate_ %f\n" %(src, dest, rate*8))
            fichier_tcl.write("$pareto_app(%s.%s) set packetSize_ %s\n" %(src, dest, taille_packet))
            fichier_tcl.write("$pareto_app(%s.%s) set shape_ %s\n" %(src, dest, shape))
            fichier_tcl.write("$pareto_app(%s.%s) attach-agent $udp_sender(%s.%s)\n" %(src, dest, src, dest))

            # planification des demarrages et arrets des agents UDP
            fichier_tcl.write("$ns at %s \"$pareto_app(%s.%s) start\"\n" %(start_date, src, dest))
            fichier_tcl.write("$ns at %s \"$pareto_app(%s.%s) stop\"\n" %(end_date, src, dest))
            flows += 1

            flow_tcp = 0 # nb flux TCP generes

            # le volume des flux temoins ne doit pas depasser le volume de la ligne actuelle
            while flow_tcp < tcp_volume :

                # volume aleatoire avec au moins 1 flux temoin (shape = 1)
                flow_volume_actual = numpy.random.zipf(a, 1)[0]
                #flow_volume_actual = random.randint(flow_tcp, tcp_volume)
               
                # Bornage de la valeur aleatoire en cas de depassement du volume cible
                if (flow_tcp + flow_volume_actual) > tcp_volume : 
                    flow_volume_actual = tcp_volume - flow_tcp

                # Generation d'une date aleatoire 
                flow_start = random.uniform(start_date, end_date)

                # Bornage de la valeur aleatoire en cas de depassement de la duree simulee
                if flow_start > simulation_duration : 
                    flow_start = retard * end_date

                # creation des agents TCP
                fichier_tcl.write("set tcp_sender(%s.%s.%s) [new Agent/TCP]\n" %(src, dest, flows))
                fichier_tcl.write("$tcp_sender(%s.%s.%s) set packetSize_ %s\n" %(src, dest, flows, taille_packet))
                # le MSS standard est de 536 octets
                fichier_tcl.write("$tcp_sender(%s.%s.%s) set windowSize_ 536\n" %(src, dest, flows))
                fichier_tcl.write("set tcp_receiver(%s.%s.%s) [new Agent/TCPSink]\n" %(src, dest, flows))

                # on place un fid afin de l'analyser avec le fichier analyze.py
                fichier_tcl.write("$tcp_sender(%s.%s.%s) set fid_ %d\n" %(src, dest, flows, flows_tcp))

                # connection des noeuds
                fichier_tcl.write("$ns attach-agent $n(%s) $tcp_sender(%s.%s.%s)\n" %(src, src, dest, flows))
                fichier_tcl.write("$ns attach-agent $n(%s) $tcp_receiver(%s.%s.%s)\n" %(dest, src, dest, flows))
                fichier_tcl.write("$ns connect $tcp_sender(%s.%s.%s) $tcp_receiver(%s.%s.%s)\n" %(src, dest, flows, src, dest, flows))

                # planification de l'envoi
                fichier_tcl.write("$ns at %s \"$tcp_sender(%s.%s.%s) send %s\"\n" %(flow_start, src, dest, flows, int(flow_volume_actual)))

                flow_tcp    += int(tcp_volume) - int(flow_volume_actual)
                flows       += 1
                flows_tcp   += 1
    
    print("%d flux temoins TCP generes" %(flows_tcp))
    return


# ouverture des differents fichiers
topology    = open(sys.argv[1], "r")
traffic     = open(sys.argv[2], "r")
fichier_tcl = open("simulation.tcl", "w")

# initialisation du fichier tcl pour la simulation
fichier_tcl.write("set ns [new Simulator]\n")

# fichier trace
fichier_tcl.write("set tracefile [open trace.tr w]\n")
fichier_tcl.write("$ns trace-all $tracefile\n")

# fichier loss
fichier_tcl.write("set loss_monitor [open loss.tr w]\n\n")

# procedure finish
fichier_tcl.write("proc finish { } {\n")
fichier_tcl.write(" global ns tracefile loss_monitor\n")
fichier_tcl.write(" $ns flush-trace\n")
fichier_tcl.write(" close $tracefile\n")
fichier_tcl.write(" close $loss_monitor\n")
fichier_tcl.write(" puts \"Simulation terminee.\"\n")
fichier_tcl.write(" exit 0\n")
fichier_tcl.write("}\n\n")

fichier_tcl.write("Node instproc getidnode { } {\n")
fichier_tcl.write("	$self instvar id_\n")
fichier_tcl.write(" return \"$id_\"\n")
fichier_tcl.write("}\n\n")

# procedure record
fichier_tcl.write("proc record {i j} {\n")
fichier_tcl.write("	global ns n monitor_queue loss_monitor\n")
fichier_tcl.write("	set now [$ns now]\n")
fichier_tcl.write("	set from_node [$n($i) getidnode]\n")
fichier_tcl.write("	set to_node [$n($j) getidnode]\n")
fichier_tcl.write("	set drop1 [$monitor_queue($i,$j) set pdrops_]\n")
fichier_tcl.write("	set drop2 [$monitor_queue($j,$i) set pdrops_]\n")
fichier_tcl.write("	set departs1 [$monitor_queue($i,$j) set pdepartures_]\n")
fichier_tcl.write("	set departs2 [$monitor_queue($j,$i) set pdrops_]\n")
fichier_tcl.write("	puts $loss_monitor \"$i $j [expr $drop1 + $drop2] [expr $departs1 + $departs2]\"\n")
fichier_tcl.write("}\n\n")

# creation topologie et trafic
create_topology(topology, fichier_tcl, 10)
create_traffic(traffic, fichier_tcl, duree_simulation, 0.5, 0.5, 1.5, 0.90, 1500)

# demarrage de la simulation
fichier_tcl.write("$ns at %s \"finish\"\n" %(duree_simulation_record))
fichier_tcl.write("puts \".................................................\"\n")
fichier_tcl.write("$ns run\n")

# fermeture fichier de sortie, traff.traf et topo.top
fichier_tcl.close()
topology.close()
traffic.close()