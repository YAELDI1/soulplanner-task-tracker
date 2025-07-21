# 🧪 Manual Testing Checklist

## 📋 Pre-Testing Setup
- [ ] Application starts without errors
- [ ] Database initializes correctly
- [ ] All UI components load properly
- [ ] Theme switching works (light/dark)

## 🎯 Core Functionality Tests

### Task Creation
- [ ] Click "+ Add Task" button opens dialog
- [ ] All form fields are visible and accessible
- [ ] Title field is required (shows validation error if empty)
- [ ] Description field accepts multi-line text
- [ ] Owner field accepts text input
- [ ] Status radio buttons work (Not Started, Working on it, Stuck, Done)
- [ ] Priority radio buttons work (Low, Medium, High, Urgent)
- [ ] Due date field accepts manual input
- [ ] Calendar picker button opens date picker
- [ ] Date picker allows selecting dates
- [ ] Estimated hours field accepts decimal numbers
- [ ] Tags field accepts comma-separated values
- [ ] Notes field accepts multi-line text
- [ ] Save button saves task and closes dialog
- [ ] Cancel button closes dialog without saving
- [ ] Close (×) button closes dialog

### Task Management
- [ ] New tasks appear in the table
- [ ] Task title is displayed correctly
- [ ] Task owner is displayed correctly
- [ ] Task status shows with correct color
- [ ] Task priority shows with correct color
- [ ] Due date is formatted correctly
- [ ] Overdue tasks show warning icon
- [ ] Today's tasks show calendar icon
- [ ] Estimated hours are displayed correctly
- [ ] Checkbox toggles task completion
- [ ] Completed tasks show checkmark
- [ ] Double-click opens edit dialog
- [ ] Edit dialog loads existing task data
- [ ] Changes are saved correctly
- [ ] Delete button shows confirmation dialog
- [ ] Confirmation dialog has Yes/No options
- [ ] Delete removes task from table

### Search and Filtering
- [ ] Search box filters tasks by title
- [ ] Search box filters tasks by description
- [ ] Search box filters tasks by owner
- [ ] Search box filters tasks by notes
- [ ] Status filter dropdown works
- [ ] Priority filter dropdown works
- [ ] Clear filters button resets all filters
- [ ] Search is case-insensitive
- [ ] Search updates results in real-time
- [ ] No results message when no matches

### Sorting
- [ ] Click column headers sorts tasks
- [ ] Sort by title (alphabetical)
- [ ] Sort by owner (alphabetical)
- [ ] Sort by status (logical order)
- [ ] Sort by priority (Low → Urgent)
- [ ] Sort by due date (chronological)
- [ ] Sort by estimated hours (numerical)
- [ ] Sort by created date (chronological)
- [ ] Click same column reverses sort order
- [ ] Sort indicator shows current sort

### Statistics
- [ ] Total tasks count is correct
- [ ] Completed tasks count is correct
- [ ] Overdue tasks count is correct
- [ ] Progress bar shows completion percentage
- [ ] Statistics update when tasks change
- [ ] Statistics reflect filtered results

## 🎨 UI/UX Tests

### Responsiveness
- [ ] Window can be resized
- [ ] Table columns adjust to window width
- [ ] Scrollbars appear when needed
- [ ] Dialog stays centered when resizing
- [ ] Text wraps properly in narrow windows
- [ ] Buttons remain accessible at all sizes

### Accessibility
- [ ] Tab key navigates through form fields
- [ ] Enter key submits forms
- [ ] Escape key closes dialogs
- [ ] Keyboard shortcuts work (Ctrl+N, Ctrl+F, etc.)
- [ ] Focus indicators are visible
- [ ] High contrast mode works
- [ ] Font sizes are readable

### Visual Design
- [ ] Modern styling is applied consistently
- [ ] Colors are appropriate for theme
- [ ] Icons are clear and meaningful
- [ ] Spacing is consistent
- [ ] Text is properly aligned
- [ ] No overlapping elements
- [ ] Loading spinner animates smoothly

## 🔧 Error Handling Tests

### Input Validation
- [ ] Empty title shows error message
- [ ] Invalid date format shows error message
- [ ] Negative hours shows error message
- [ ] Very long text shows error message
- [ ] Error messages are clear and helpful
- [ ] Form stays open after validation error
- [ ] Save button is re-enabled after error

### Database Errors
- [ ] Application handles database connection errors
- [ ] Application handles disk space errors
- [ ] Application handles permission errors
- [ ] Error dialogs show helpful messages
- [ ] Application doesn't crash on database errors
- [ ] Data is not lost during errors

### Network/System Errors
- [ ] Application handles file system errors
- [ ] Application handles memory errors
- [ ] Application handles permission errors
- [ ] Application gracefully handles system errors

## ⚡ Performance Tests

### Loading
- [ ] Application starts within 5 seconds
- [ ] Task dialog opens within 1 second
- [ ] Table loads 100+ tasks within 3 seconds
- [ ] Search responds within 500ms
- [ ] No UI freezing during operations

### Memory Usage
- [ ] Memory usage doesn't grow excessively
- [ ] No memory leaks after creating/deleting tasks
- [ ] Application remains responsive with many tasks

### Concurrency
- [ ] Multiple dialogs can be opened
- [ ] Background operations don't block UI
- [ ] Loading indicators show during long operations

## 🔄 Edge Cases

### Data Edge Cases
- [ ] Very long task titles (100+ characters)
- [ ] Very long descriptions (1000+ characters)
- [ ] Special characters in text fields
- [ ] Unicode characters in text fields
- [ ] Empty/null values in database
- [ ] Corrupted database files
- [ ] Very old dates (1900s)
- [ ] Very future dates (2100s)

### User Interaction Edge Cases
- [ ] Rapid clicking on buttons
- [ ] Multiple rapid form submissions
- [ ] Closing dialogs while saving
- [ ] Resizing window during operations
- [ ] Switching themes during operations
- [ ] Minimizing/maximizing during operations

### System Edge Cases
- [ ] Low disk space
- [ ] Low memory
- [ ] High CPU usage
- [ ] Network interruptions
- [ ] System sleep/wake cycles

## 📱 Cross-Platform Tests

### Windows Specific
- [ ] Application runs on Windows 10/11
- [ ] Windows theme integration works
- [ ] File paths handle Windows separators
- [ ] Windows shortcuts work (Ctrl+C, Ctrl+V, etc.)

### Resolution Tests
- [ ] Application works on 1920x1080
- [ ] Application works on 1366x768
- [ ] Application works on 4K displays
- [ ] Application works on high DPI displays

## 🧹 Cleanup Tests

### Data Persistence
- [ ] Tasks are saved between application restarts
- [ ] Settings are preserved between restarts
- [ ] Theme preference is remembered
- [ ] Window size/position is remembered

### Data Integrity
- [ ] No data corruption after crashes
- [ ] No duplicate tasks created
- [ ] No orphaned data in database
- [ ] Database backup/restore works

## 📊 Test Results Template

```
Test Date: _______________
Tester: _________________
Application Version: _______

✅ Passed: ___
❌ Failed: ___
⚠️ Issues: ___

Critical Issues:
1. _________________
2. _________________

Minor Issues:
1. _________________
2. _________________

Recommendations:
1. _________________
2. _________________

Overall Assessment: ⭐⭐⭐⭐⭐ (1-5 stars)
```

## 🚀 Quick Test Commands

```bash
# Run automated tests
python run_tests.py

# Run specific test categories
python -c "from test_app import run_component_tests; run_component_tests()"
python -c "from test_app import run_functionality_tests; run_functionality_tests()"

# Start application for manual testing
python main.py
```

## 📝 Bug Reporting Template

```
Bug Title: [Brief description]

Severity: [Critical/High/Medium/Low]

Steps to Reproduce:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Expected Behavior:
[What should happen]

Actual Behavior:
[What actually happens]

Environment:
- OS: [Windows 10/11]
- Python Version: [3.8+]
- Application Version: [2.0.0]

Screenshots:
[If applicable]

Additional Notes:
[Any other relevant information]
``` 