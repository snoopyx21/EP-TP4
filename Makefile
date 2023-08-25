PYTHON = python
NS2 = ns

simulator: execution
	$(NS2) simulation.tcl

execution: simulation.py topo.top traff.traf
	$(PYTHON) simulation.py topo.top traff.traf

clean:
	rm -f simulation.tcl trace.tr loss.tr time.txt loss_results.txt analyze.txt

analyze: loss.py analyze.py
	$(PYTHON) loss.py
	$(PYTHON) analyze.py

archive:
	tar cvf DIVRIOTIS_Constantin.tar.gz Makefile simulation.py topo.top traff.traf loss.py analyze.py evalutation_performance_DIVRIOTIS.pdf