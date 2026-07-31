# ---- User-configurable -------------------------------------------------

# Name of the top-level module
TOP      = mkInfAndNaNFlagger_TB

# Directory for build artifacts
BDIR     = build

# Folders to search for imports
BSV_DIRS = .

# Build Bluespec search path (single argument, colon-separated)
#BSV_PATH = +:$(subst  ,:,${BSV_DIRS})
BSV_PATH = +:


# Explicit list of all BSV files your build needs
BSV_SRCS = \
	   InfAndNaNFlagger.bsv \
           InfAndNaNFlagger_TB.bsv

# The specific testbench (the one containing $(TOP))
TB_BSV   = InfAndNaNFlagger_TB.bsv

# Executable output name
EXEC     = $(BDIR)/$(TOP)

# ------------------------------------------------------------------------

all: $(EXEC)

$(BDIR):
	mkdir -p $(BDIR)

# Step 1: Compile to .ba
$(BDIR)/$(TOP).ba: $(BSV_SRCS) | $(BDIR)
	bsc -sim -u -g $(TOP) -bdir $(BDIR) -p $(BSV_PATH) $(TB_BSV)

# Step 2: Link Bluesim executable
$(EXEC): $(BDIR)/$(TOP).ba
	bsc -sim -e $(TOP) -bdir $(BDIR) -simdir $(BDIR) -o $(EXEC)

run: $(EXEC)
	./$(EXEC)

clean:
	rm -rf $(BDIR)
