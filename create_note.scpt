#!/usr/bin/osascript

on run argv
    set unixPath to item 1 of argv
    do shell script "sed 's/$/<br>/' '" & unixPath & "' > /tmp/tmp"
    set bodytext to read POSIX file "/tmp/tmp"
    do shell script "rm -f /tmp/tmp"
    
    tell application "Notes"
        tell account "iCloud"
            make new note at folder "Notes" with properties {name:unixPath, body:bodytext}
        end tell
    end tell
end run
