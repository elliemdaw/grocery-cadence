on run {list_name, output_path}
    set dateThreshold to (current date) - (365 * days)

    tell application "Reminders"
        set groceryList to list list_name
        set completedItems to (every reminder in groceryList whose completed is true and completion date > dateThreshold)
        
        set outputContent to "item,completion_date" & return -- Collect all the content in memory
        repeat with anItem in completedItems
            set itemName to name of anItem
            set completionDate to completion date of anItem
            set csvLine to itemName & "," & (completionDate as «class isot» as string) & return
            set outputContent to outputContent & csvLine -- Append to the outputContent string
        end repeat
        
        set outputFile to output_path as POSIX file
        set fileRef to open for access outputFile with write permission
        write outputContent to fileRef -- Write everything at once
        close access fileRef
    end tell
end run