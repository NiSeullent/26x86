SRC_DIR   := src
BUILD_DIR := build
DYLIB     := $(BUILD_DIR)/libExtremeCompositorInterpose.dylib
PLUGIN    := $(BUILD_DIR)/ExtremeCompositor.dylib

CC        ?= clang
CFLAGS    ?= -Wall -Wextra -O2 -fPIC
LDFLAGS_DYLIB := -dynamiclib -install_name @rpath/libExtremeCompositorInterpose.dylib
FRAMEWORKS := -framework CoreGraphics -framework ColorSync -framework CoreFoundation

.PHONY: all clean plugin dirs

all: dirs $(DYLIB)

dirs:
	@mkdir -p $(BUILD_DIR)

$(DYLIB): $(SRC_DIR)/ExtremeCompositorInterpose.c $(SRC_DIR)/ExtremeCompositorInterpose.h
	$(CC) $(CFLAGS) $(LDFLAGS_DYLIB) $(FRAMEWORKS) -o $@ $(SRC_DIR)/ExtremeCompositorInterpose.c

plugin: dirs $(PLUGIN)

$(PLUGIN): $(SRC_DIR)/ExtremeCompositorInterpose.c $(SRC_DIR)/SkyLightPluginShim.c $(SRC_DIR)/ExtremeCompositorInterpose.h
	$(CC) $(CFLAGS) -dynamiclib -install_name @rpath/ExtremeCompositor.dylib $(FRAMEWORKS) -o $@ $(SRC_DIR)/ExtremeCompositorInterpose.c $(SRC_DIR)/SkyLightPluginShim.c

clean:
	rm -rf $(BUILD_DIR)
