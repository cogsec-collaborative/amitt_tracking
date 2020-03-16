This is a manual process with instructions created from Andy Patel’s video at 
https://www.youtube.com/watch?time_continue=17&v=AqlT0khVuZA

* Get Gephi from https://gephi.org/users/download/ - install it.
* Start Gephi.
* Click on top menu>file>“import spreadsheet”. Grab User_user_graph.csv - use all defaults
* Top menu: Go to data laboratory, “copy data to another column”, click ‘id’,  click okay.
* Go to overview.  RHS: Run modularity algorithm, using defaults
* RHS: Run average weighted degree algorithm
* LHS: Click color icon, then partition, modularity class. Open palette, generate, unclick “limit number of colors”, preset=intense, generate, okay
* LHS: Select “tt”, ranking, weighted degree, set minsize=0.2, choose 3rd spline, apply
* LHS: Layout: OpenOrd, run. Then forceatlas2, run. Try stronger gravity, and scaling=200
* Top menu: Preview - select “black background”, click “refresh”. Click “Reset zoom”

Gephi has an API - these tasks could be automated.
