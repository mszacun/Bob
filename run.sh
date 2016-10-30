#!/usr/bin/env sh

NUMBER_OF_PANES=`tmux list-panes | wc -l`
if [ "$NUMBER_OF_PANES" -lt "3" ]; then
    tmux split-window -h -t:.0
    tmux split-window -t:.1
fi

tmux send-keys -t :.1 "(cd ~/bob; python2 bob.py -l)"
tmux send-keys -t :.1 Enter
sleep 0.3

tmux send-keys -t :.2 "(cd ~/bob; python2 bob.py)"
tmux send-keys -t :.2 Enter

tmux select-pane -t :.2

# map <leader>r :!sh ~/bob/run.sh<CR>
