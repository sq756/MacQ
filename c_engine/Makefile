# MacQ C Engine Makefile
# Mac-Native Quantum Computing Software
# Copyright (c) 2026 MacQ Development Team

# Compiler and flags
CC = clang
CFLAGS = -O3 -Wall -Wextra -std=c11
CFLAGS += -I./include

# macOS specific: link Accelerate framework
LDFLAGS = -framework Accelerate
LDFLAGS += -lm

# For shared library
SHARED_FLAGS = -dynamiclib -fPIC

# Directories
SRC_DIR = src
INC_DIR = include
TEST_DIR = tests
BUILD_DIR = build

# Source files
SOURCES = $(SRC_DIR)/macq.c
OBJECTS = $(SOURCES:.c=.o)

# Targets
DYLIB = libmacq.dylib
TEST_EXEC = test_macq

# Universal binary for both Intel and Apple Silicon
ARCH_FLAGS = -arch arm64 -arch x86_64

# Default target
all: $(DYLIB)

# Build shared library (universal binary)
$(DYLIB): $(SOURCES)
	@echo "Building MacQ C Engine (universal binary for arm64 + x86_64)..."
	$(CC) $(CFLAGS) $(ARCH_FLAGS) $(SHARED_FLAGS) -o $@ $(SOURCES) $(LDFLAGS)
	@echo "✓ Built $@ successfully"
	@file $@

# Build shared library (native arch only, faster compilation)
native: $(SOURCES)
	@echo "Building MacQ C Engine (native architecture only)..."
	$(CC) $(CFLAGS) $(SHARED_FLAGS) -o $(DYLIB) $(SOURCES) $(LDFLAGS)
	@echo "✓ Built $(DYLIB) successfully"

# Debug build
debug: CFLAGS += -g -DDEBUG -O0
debug: $(DYLIB)
	@echo "✓ Built debug version"

# Build and run tests
test: $(DYLIB)
	@echo "Building and running tests..."
	$(CC) $(CFLAGS) -o $(TEST_EXEC) $(TEST_DIR)/test_macq.c -L. -lmacq -Wl,-rpath,@loader_path
	@echo "✓ Tests compiled successfully"
	@echo "Running tests..."
	./$(TEST_EXEC)

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -f $(DYLIB) $(OBJECTS) $(TEST_EXEC)
	rm -rf *.dSYM
	@echo "✓ Clean complete"

# Install library (copy to /usr/local/lib)
install: $(DYLIB)
	@echo "Installing $(DYLIB) to /usr/local/lib..."
	sudo cp $(DYLIB) /usr/local/lib/
	sudo cp $(INC_DIR)/macq.h /usr/local/include/
	@echo "✓ Installation complete"

# Uninstall
uninstall:
	@echo "Uninstalling MacQ..."
	sudo rm -f /usr/local/lib/$(DYLIB)
	sudo rm -f /usr/local/include/macq.h
	@echo "✓ Uninstallation complete"

# Check library symbols
check: $(DYLIB)
	@echo "Checking exported symbols..."
	nm -gU $(DYLIB) | grep qstate

# Check architecture
arch-check: $(DYLIB)
	@echo "Checking supported architectures..."
	lipo -info $(DYLIB)

# Print help
help:
	@echo "MacQ C Engine Build System"
	@echo "=========================="
	@echo "Targets:"
	@echo "  all        - Build universal library (arm64 + x86_64)"
	@echo "  native     - Build for native architecture only (faster)"
	@echo "  debug      - Build with debug symbols"
	@echo "  test       - Build and run test suite"
	@echo "  clean      - Remove build artifacts"
	@echo "  install    - Install library system-wide"
	@echo "  uninstall  - Remove installed library"
	@echo "  check      - Check exported symbols"
	@echo "  arch-check - Check supported architectures"
	@echo "  help       - Show this help message"

.PHONY: all native debug test clean install uninstall check arch-check help
