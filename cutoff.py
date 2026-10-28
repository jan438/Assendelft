def cutoff(crdo, crdi, points):
    print(crdo, crdi)
	if crdo[1] < points[0] and crdo[1] > points[2] and crdo[0] > points[3]:
		crdo[1] = crdo[1] + abs(crdi[1] - crdo[1]) / 2
		crdo[0] = points[3]
	if crdo[0] < points[3] and crdo[0] > points[1] and crdo[1] > points[0]:
		crdo[0] = crdo[0] + abs(crdi[0] - crdo[0]) / 2
		crdo[1] = points[0]
    print(crdo, crdi)
    return crdo
    
          firstcrdo = cutoff(firstcrdo, firstcrdi, points)
    crds.append(firstcrdo)
     
              break
          lastcrdo = cutoff(lastcrdo, lastcrdi, points)
        
    loop
    
    crds.append(lastcrdo)
   