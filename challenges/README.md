# 2D Peak Element & Anagram Grouping Challenges

This repository contains solutions for two algorithmic challenges:

1. **Find Peak Element in a 2D Matrix**
2. **Group Anagrams and Find Largest Group**

## Files
- `challenges.py`: Contains all the functions and test cases.

## How to Run

1. Make sure you have Python 3 installed (Python 3.6+ recommended).
2. Open a terminal and navigate to the project directory.
3. Run the following command:

```bash
python challenges.py
```

This will execute the test cases for both challenges and print the results to the terminal.

## Function Descriptions

### 1. `find_peak_element_2d(matrix)`
- Efficiently finds a peak element in a 2D matrix (greater than or equal to its up, down, left, and right neighbors).
- Returns the coordinates `(row, col)` of any peak element.
- Handles edge cases (single element, single row/column).

### 2. `analyze_anagrams(words)`
- Groups words that are anagrams (case-insensitive).
- Returns a dictionary with the largest group and the total number of groups.

### 3. `get_all_anagram_groups(words)`
- Returns a list of all anagram groups (case-insensitive).

## Example Usage

See the bottom of `challenges.py` for sample test cases and expected outputs.

---

Feel free to modify or extend the code for your own use! 