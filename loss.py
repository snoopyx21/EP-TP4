import numpy as np

trace = open("loss.tr","r")

# declaration des variables 
# pertes est un tableau comportant tous les noeuds
pertes = np.zeros(shape=(26,26))
total = 0
total_indice = 0

# parcours du fichier loss.tr
for line in trace :
    stripped = line.strip()
    if not stripped :
        continue
    else :
		temp = stripped.split(' ')

		noeud1 	= int(temp[0])
		noeud2 	= int(temp[1])
		loss 	= int(temp[2])
		data 	= int(temp[3])
		pertes[noeud1][noeud2] += loss
		total += loss
		if loss > 0 :
			total_indice += 1

imax = [0] * 3
jmax = [0] * 3
valmax = [0] * 3

for i in range(len(pertes)) :
	for j in range(len(pertes[i])):
		if pertes[i][j] > valmax[0]:
			if pertes[i][j] > valmax[1]:
				if pertes[i][j] > valmax[2]:
					# perte nouveau max - on compare les valmax
					if valmax[0] > valmax[1]:
						if valmax[0] > valmax[2]:

							if valmax[1] > valmax[2]:
								valmax[2] = pertes[i][j]
								imax[2] = i
								jmax[2] = j

							else:
								valmax[1] = pertes[i][j]
								imax[1] = i
								jmax[1] = j

						elif valmax[2] > valmax[0]:
							valmax[1] = pertes[i][j]
							imax[1] = i
							jmax[1] = j


					elif valmax[1] > valmax[0]:
						if valmax[1] > valmax[2]:
							if valmax[0] > valmax[2]:
								valmax[2] = pertes[i][j]
								imax[2] = i
								jmax[2] = j
							else:
								valmax[0] = pertes[i][j]
								imax[0] = i
								jmax[0] = j
						elif valmax[2] > valmax[0]:
								valmax[1] = pertes[i][j]
								imax[1] = i
								jmax[1] = j
					else:
						valmax[0] = pertes[i][j]
						imax[0] = i
						jmax[0] = j

				elif valmax[0] > valmax[1]:
						valmax[1] = pertes[i][j]
						imax[1] = i
						jmax[1] = j
				else:
					valmax[0] = pertes[i][j]
					imax[0] = i
					jmax[0] = j
			elif pertes[i][j] > valmax[2]:
				if valmax[0] > valmax[2]:
					valmax[2] = pertes[i][j]
					imax[2] = i
					jmax[2] = j
				else:
					valmax[0] = pertes[i][j]
					imax[0] = i
					jmax[0] = j
		elif pertes[i][j] > valmax[1]:
			if pertes[i][j] > valmax[2]:
				if valmax[1] > valmax[2]:
					valmax[2] = pertes[i][j]
					imax[2] = i
					jmax[2] = j
				else:
					valmax[1] = pertes[i][j]
					imax[1] = i
					jmax[1] = j
		elif pertes[i][j] > valmax[2]:
			valmax[2] = pertes[i][j]
			imax[2] = i
			jmax[2] = j


# ecriture des resultats dans un fichier loss_results
output  = open("loss_results.txt", "w")

output.write("Les 3 liens les \"plus faibles\" sont:\n")
output.write("\t%s-%s avec %s octets perdus\n" %(imax[0], jmax[0], valmax[0]))
output.write("\t%s-%s avec %s octets perdus\n" %(imax[1], jmax[1], valmax[1]))
output.write("\t%s-%s avec %s octets perdus\n" %(imax[2], jmax[2], valmax[2]))
output.write("\n")
output.write("Pourcentage de pertes par liens :\n")
for i in range(len(pertes)) :
	for j in range(len(pertes[i])):
		if ( pertes[i][j] + pertes[j][i] != 0 ) :
			pourcent = ((pertes[i][j]+pertes[j][i]) / (total)) * 100
			output.write("\tLien %s-%s : %s\n" %(i,j,pourcent))
output.write("\t%s pertes totales dans le fichier\n" %(total))
trace.close()
output.close()