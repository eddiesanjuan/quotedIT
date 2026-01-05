#!/bin/bash
# Worktree Management Script for Quoted Autonomous Operations
# DISC-104: Work isolation via git worktrees
#
# Usage:
#   ./scripts/worktree.sh create <ticket-id>   - Create worktree for ticket
#   ./scripts/worktree.sh complete <ticket-id> - Complete and clean up
#   ./scripts/worktree.sh abort <ticket-id>    - Abort and discard changes
#   ./scripts/worktree.sh list                 - List active worktrees
#   ./scripts/worktree.sh prune                - Clean up stale worktrees

set -e

# Configuration
REPO_ROOT="/Users/eddiesanjuan/Personal_Assistant/Eddie_Personal_Assistant/quoted"
WORKTREE_BASE="/tmp/quoted-worktrees"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Ensure worktree base directory exists
ensure_worktree_base() {
    if [ ! -d "$WORKTREE_BASE" ]; then
        mkdir -p "$WORKTREE_BASE"
        log_info "Created worktree base directory: $WORKTREE_BASE"
    fi
}

# Create a new worktree for a ticket
create_worktree() {
    local ticket_id="$1"
    if [ -z "$ticket_id" ]; then
        log_error "Ticket ID required. Usage: worktree.sh create <ticket-id>"
        exit 1
    fi

    ensure_worktree_base

    local worktree_path="$WORKTREE_BASE/$ticket_id"
    local branch_name="feat/${ticket_id,,}"  # lowercase

    # Check if worktree already exists
    if [ -d "$worktree_path" ]; then
        log_warn "Worktree already exists at $worktree_path"
        echo "Use 'worktree.sh abort $ticket_id' to remove it first"
        exit 1
    fi

    # Check if branch already exists
    if git -C "$REPO_ROOT" show-ref --verify --quiet "refs/heads/$branch_name"; then
        log_info "Branch $branch_name exists, creating worktree from it"
        git -C "$REPO_ROOT" worktree add "$worktree_path" "$branch_name"
    else
        log_info "Creating new branch $branch_name from main"
        git -C "$REPO_ROOT" worktree add -b "$branch_name" "$worktree_path" main
    fi

    log_info "Worktree created at: $worktree_path"
    log_info "Branch: $branch_name"
    echo ""
    echo "To work in this worktree:"
    echo "  cd $worktree_path"
}

# Complete work and clean up worktree
complete_worktree() {
    local ticket_id="$1"
    if [ -z "$ticket_id" ]; then
        log_error "Ticket ID required. Usage: worktree.sh complete <ticket-id>"
        exit 1
    fi

    local worktree_path="$WORKTREE_BASE/$ticket_id"
    local branch_name="feat/${ticket_id,,}"

    if [ ! -d "$worktree_path" ]; then
        log_error "Worktree not found at $worktree_path"
        exit 1
    fi

    # Check for uncommitted changes
    if [ -n "$(git -C "$worktree_path" status --porcelain)" ]; then
        log_warn "Worktree has uncommitted changes:"
        git -C "$worktree_path" status --short
        echo ""
        read -p "Commit remaining changes? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Please commit changes before completing"
            exit 1
        fi
    fi

    # Check if changes are pushed
    local local_hash=$(git -C "$worktree_path" rev-parse HEAD)
    local remote_hash=$(git -C "$worktree_path" rev-parse "origin/$branch_name" 2>/dev/null || echo "")

    if [ "$local_hash" != "$remote_hash" ]; then
        log_info "Pushing changes to origin..."
        git -C "$worktree_path" push -u origin "$branch_name"
    fi

    # Remove worktree
    log_info "Removing worktree..."
    git -C "$REPO_ROOT" worktree remove "$worktree_path"

    log_info "Worktree completed and removed"
    log_info "Branch $branch_name remains on remote for PR"
}

# Abort work and discard all changes
abort_worktree() {
    local ticket_id="$1"
    if [ -z "$ticket_id" ]; then
        log_error "Ticket ID required. Usage: worktree.sh abort <ticket-id>"
        exit 1
    fi

    local worktree_path="$WORKTREE_BASE/$ticket_id"
    local branch_name="feat/${ticket_id,,}"

    if [ ! -d "$worktree_path" ]; then
        log_warn "Worktree not found at $worktree_path"
        # Still try to clean up branch
    else
        log_info "Removing worktree (force)..."
        git -C "$REPO_ROOT" worktree remove --force "$worktree_path"
    fi

    # Optionally delete local branch
    if git -C "$REPO_ROOT" show-ref --verify --quiet "refs/heads/$branch_name"; then
        log_info "Deleting local branch $branch_name..."
        git -C "$REPO_ROOT" branch -D "$branch_name"
    fi

    log_info "Worktree aborted and cleaned up"
}

# List all active worktrees
list_worktrees() {
    log_info "Active worktrees:"
    echo ""
    git -C "$REPO_ROOT" worktree list
    echo ""

    # Show any orphaned worktree directories
    if [ -d "$WORKTREE_BASE" ]; then
        local orphans=""
        for dir in "$WORKTREE_BASE"/*/; do
            if [ -d "$dir" ]; then
                local ticket=$(basename "$dir")
                if ! git -C "$REPO_ROOT" worktree list | grep -q "$dir"; then
                    orphans="$orphans  $dir\n"
                fi
            fi
        done
        if [ -n "$orphans" ]; then
            log_warn "Orphaned directories (not linked to git):"
            echo -e "$orphans"
            echo "Run 'worktree.sh prune' to clean up"
        fi
    fi
}

# Prune stale worktrees
prune_worktrees() {
    log_info "Pruning stale worktrees..."
    git -C "$REPO_ROOT" worktree prune

    # Also clean up any orphaned directories
    if [ -d "$WORKTREE_BASE" ]; then
        for dir in "$WORKTREE_BASE"/*/; do
            if [ -d "$dir" ]; then
                if ! git -C "$REPO_ROOT" worktree list | grep -q "$dir"; then
                    log_info "Removing orphaned directory: $dir"
                    rm -rf "$dir"
                fi
            fi
        done
    fi

    log_info "Prune complete"
}

# Main command router
case "${1:-}" in
    create)
        create_worktree "$2"
        ;;
    complete)
        complete_worktree "$2"
        ;;
    abort)
        abort_worktree "$2"
        ;;
    list)
        list_worktrees
        ;;
    prune)
        prune_worktrees
        ;;
    *)
        echo "Worktree Management for Quoted Autonomous Operations"
        echo ""
        echo "Usage:"
        echo "  $0 create <ticket-id>   Create worktree for ticket (e.g., disc-104)"
        echo "  $0 complete <ticket-id> Complete work and clean up"
        echo "  $0 abort <ticket-id>    Abort and discard all changes"
        echo "  $0 list                 List active worktrees"
        echo "  $0 prune                Clean up stale worktrees"
        echo ""
        echo "Examples:"
        echo "  $0 create disc-104"
        echo "  $0 complete disc-104"
        echo "  $0 abort disc-104"
        exit 1
        ;;
esac
