# ---- User-configurable -------------------------------------------------

# Name of the top-level module
TOP      = mkComparator_tb

# Directory for build artifacts
BDIR     = build

# Explicit list of all BSV files your build needs
BSV_SRCS = \
    Comparator.bsv \
    Comparator_tb.bsv

# The specific testbench (the one containing $(TOP))
TB_BSV   = Comparator_tb.bsv

# Executable output name
EXEC     = $(BDIR)/$(TOP)

# ------------------------------------------------------------------------

all: $(EXEC)

$(BDIR):
	mkdir -p $(BDIR)

# Step 1: Compile to .ba
$(BDIR)/$(TOP).ba: $(BSV_SRCS) | $(BDIR)
	bsc -sim -u -g $(TOP) -bdir $(BDIR) $(TB_BSV)

# Step 2: Link Bluesim executable
$(EXEC): $(BDIR)/$(TOP).ba
	bsc -sim -e $(TOP) -bdir $(BDIR) -simdir $(BDIR) -o $(EXEC)

run: $(EXEC)
	./$(EXEC)

clean:
	rm -rf $(BDIR)
