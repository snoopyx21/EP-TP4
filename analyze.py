import numpy as np

trace = open("trace.tr","r")

# duree simulation
duree_simu = 900

# declaration des differentes variables
pareto_send_data = 0
pareto_send_count = 0
tcp_send_data = 0
tcp_send_count = 0

pareto_lost_data = 0
pareto_lost_count = 0
tcp_lost_data = 0
tcp_lost_count = 0

pareto_received_data = 0
pareto_received_count = 0
tcp_received_data = 0
tcp_received_count = 0

# generation de 1500 flux max
tcp_flows_send_count = np.zeros(shape=(1500))
tcp_flows_send_data = np.zeros(shape=(1500))
tcp_flows_lost_count = np.zeros(shape=(1500))
tcp_flows_lost_data = np.zeros(shape=(1500))

# parcours du fichier trace
for line in trace :
    stripped = line.strip()
    if not stripped :
        continue
    else :
        temp = stripped.split(' ')

		# traitement des differents cas possibles
        if temp[0] == '+' :
            if temp[4] == 'pareto':
                pareto_send_data += int(temp[5])
                pareto_send_count += 1

            if temp[4] == 'tcp':
                tcp_send_data += int(temp[5])
                tcp_send_count += 1
                tcp_flows_send_data[int(temp[7])] += int(temp[5])
                tcp_flows_send_count[int(temp[7])] += 1
        
        if temp[0] == 'r' :
            if temp[4] == 'pareto':
                pareto_received_data += int(temp[5])
                pareto_received_count += 1

            if temp[4] == 'tcp':
                tcp_received_data += int(temp[5])
                tcp_received_count+= 1

        if temp[0] == 'd' :
            if temp[4] == 'pareto':
                pareto_lost_data += int(temp[5])
                pareto_lost_count += 1
            if temp[4] == 'tcp':
                tcp_lost_data += int(temp[5])
                tcp_lost_count+= 1
                tcp_flows_lost_data[int(temp[7])] += int(temp[5])
                tcp_flows_lost_count[int(temp[7])] += 1

trace.close()
# incription des resultats dans le fichier analyze.txt
output  = open("analyze.txt", "w")

# traitement des resultats pareto et tcp
output.write("Trafic de fond Pareto :\n")
output.write("%s paquets envoyes en %s octets\n" %(float(pareto_send_count), float(pareto_send_data)) )
output.write("%s paquets recus en %s octets\n" %(float(pareto_received_count), float(pareto_received_data)))
output.write("%s paquets perdus en %s octets\n" %(float(pareto_lost_count), float(pareto_lost_data)))

output.write("\nTrafic temoin TCP :\n")
output.write("%s paquets envoyes en %s octets\n" %(float(tcp_send_count), float(tcp_send_data)))
output.write("%s paquets recus en %s octets\n" %(float(tcp_received_count), float(tcp_received_data)))
output.write("%s paquets perdus en %s octets\n" %(float(tcp_lost_count), float(tcp_lost_data)))

# traitement des resultats globaux
proportion_pareto = ( float(pareto_received_data) /(tcp_received_data+pareto_received_data) ) * 100
proportion_tcp = (float(tcp_received_data)/float((tcp_received_data+pareto_received_data))) *100
throughput = (pareto_send_count+tcp_send_count) / duree_simu
loss = (float(tcp_lost_data) / float(tcp_send_data)) *100
paquet_recu = float(pareto_received_count) + float(tcp_received_count)
paquet_recu_mo = paquet_recu / float(1000000)
output.write("\n%s paquets envoyes dont %s (%f Mo) remis avec succes\n" %((float(pareto_send_count)+float(tcp_send_count)), paquet_recu, paquet_recu_mo))
output.write("Proportion de trafic de fond Pareto %s pourcent\n" %(proportion_pareto))
output.write("Proportion de trafic temoin TCP %s pourcent\n" %(proportion_tcp) )
output.write("Debit %s octets/s pour une simulation de %s secondes\nTaux de perte de %f pourcent \n" %(throughput,duree_simu, loss) )
output.write("Pertes trafic de fond Pareto %f\n" %(float(pareto_lost_data)/float(pareto_send_data)*100))
output.write("Pertes trafic des flux temoins TCP %f\n" %(float(tcp_lost_data)/float(tcp_send_data)*100))


# creation de tableaux contenat les pires flux
imax = [0] * 3
valmax = [0] * 3

for i in range(len(tcp_flows_lost_count)):
		if tcp_flows_lost_count[i] > valmax[0]:
			if tcp_flows_lost_count[i] > valmax[1]:
				if tcp_flows_lost_count[i] > valmax[2]:
					# perte nouveau max - on compare les valmax
					if valmax[0] > valmax[1]:
						if valmax[0] > valmax[2]:
							if valmax[1] > valmax[2]:
								valmax[2] = tcp_flows_lost_count[i]
								imax[2] = i
							else:
								valmax[1] = tcp_flows_lost_count[i]
								imax[1] = i
						elif valmax[2] > valmax[0]:
							valmax[1] = tcp_flows_lost_count[i]
							imax[1] = i
					elif valmax[1] > valmax[0]:
						if valmax[1] > valmax[2]:
							if valmax[0] > valmax[2]:
								valmax[2] = tcp_flows_lost_count[i]
								imax[2] = i						
							else:
								valmax[0] = tcp_flows_lost_count[i]
								imax[0] = i					
						elif valmax[2] > valmax[0]:
								valmax[1] = tcp_flows_lost_count[i]
								imax[1] = i				
					else:
						valmax[0] = tcp_flows_lost_count[i]
						imax[0] = i					
				elif valmax[0] > valmax[1]:
						valmax[1] = tcp_flows_lost_count[i]
						imax[1] = i					
				else:
					valmax[0] = tcp_flows_lost_count[i]
					imax[0] = i				
			elif tcp_flows_lost_count[i] > valmax[2]:
				if valmax[0] > valmax[2]:
					valmax[2] = tcp_flows_lost_count[i]
					imax[2] = i				
				else:
					valmax[0] = tcp_flows_lost_count[i]
					imax[0] = i				
		elif tcp_flows_lost_count[i] > valmax[1]:
			if tcp_flows_lost_count[i] > valmax[2]:
				if valmax[1] > valmax[2]:
					valmax[2] = tcp_flows_lost_count[i]
					imax[2] = i				
				else:
					valmax[1] = tcp_flows_lost_count[i]
					imax[1] = i				
		elif tcp_flows_lost_count[i] > valmax[2]:
			valmax[2] = tcp_flows_lost_count[i]
			imax[2] = i
		
# ecriture des pires flux trouves dans le fichier
output.write("\n\n*********************************************************************\n\n")
output.write("Les 3 flux les \"plus faibles\" sont:\n")
output.write("\tFlux %s avec %s octets perdus\n" %(imax[0], valmax[0]))
output.write("\tFlux %s avec %s octets perdus\n" %(imax[1], valmax[1]))
output.write("\tFlux %s avec %s octets perdus\n" %(imax[2], valmax[2]))
output.write("\n")
output.write("Pourcentage d'octets par liens :\n")
for i in range(len(tcp_flows_lost_count)) :
		if ( tcp_flows_lost_count[i] + tcp_flows_lost_count[i] != 0 ) :
			pourcent = ((tcp_flows_lost_count[i]+tcp_flows_lost_count[i]) / (tcp_lost_count)) * 100
			output.write("\tFlux %s : %s\n" %(i,pourcent))

output.close()