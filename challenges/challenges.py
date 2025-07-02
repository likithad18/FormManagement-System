# =====================
# Challenge 1: Find Peak Elements in 2D Matrix
# =====================
def find_peak_element_2d(matrix):
    """
    Return (row, col) of any peak element in a 2D matrix.
    A peak is an element greater than or equal to its neighbors (up, down, left, right).
    Edges are considered as negative infinity.
    """
    if not matrix or not matrix[0]:
        return None
    n, m = len(matrix), len(matrix[0])
    
    def get_val(r, c):
        if 0 <= r < n and 0 <= c < m:
            return matrix[r][c]
        return float('-inf')

    # Binary search on columns for efficiency
    left, right = 0, m - 1
    while left <= right:
        mid_col = (left + right) // 2
        # Find the row with the max element in this column
        max_row = max(range(n), key=lambda r: matrix[r][mid_col])
        mid_val = matrix[max_row][mid_col]
        left_val = get_val(max_row, mid_col - 1)
        right_val = get_val(max_row, mid_col + 1)
        if mid_val >= left_val and mid_val >= right_val:
            return (max_row, mid_col)
        elif left_val > mid_val:
            right = mid_col - 1
        else:
            left = mid_col + 1
    return None

# =====================
# Challenge 2: Group Anagrams and Find Largest Group
# =====================
def analyze_anagrams(words):
    """
    Group anagrams, return the largest group and total number of groups.
    Case insensitive.
    """
    from collections import defaultdict
    groups = defaultdict(list)
    for word in words:
        key = ''.join(sorted(word.lower()))
        groups[key].append(word)
    all_groups = list(groups.values())
    largest_group = max(all_groups, key=len) if all_groups else []
    return {"largest_group": largest_group, "total_groups": len(all_groups)}


def get_all_anagram_groups(words):
    """
    Return a list of all anagram groups (each group is a list of words).
    Case insensitive.
    """
    from collections import defaultdict
    groups = defaultdict(list)
    for word in words:
        key = ''.join(sorted(word.lower()))
        groups[key].append(word)
    return list(groups.values())


if __name__ == "__main__":
    # =====================
    # Challenge 1: Find Peak Elements in 2D Matrix - Test Cases
    # =====================
    print("Challenge 1: Find Peak Elements in 2D Matrix\n")
    matrix1 = [
        [1, 3, 20, 4, 1],
        [2, 5, 10, 9, 3],
        [15, 6, 7, 8, 18],
        [4, 10, 11, 12, 9]
    ]
    print("matrix1 peak:", find_peak_element_2d(matrix1))

    matrix2 = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    print("matrix2 peak:", find_peak_element_2d(matrix2))

    matrix3 = [[5]]
    print("matrix3 peak:", find_peak_element_2d(matrix3))

    matrix4 = [
        [10, 8, 10, 10],
        [14, 13, 12, 11],
        [15, 9, 11, 21],
        [16, 17, 19, 20]
    ]
    print("matrix4 peak:", find_peak_element_2d(matrix4))

    # =====================
    # Challenge 2: Group Anagrams and Find Largest Group - Test Cases
    # =====================
    print("\nChallenge 2: Group Anagrams and Find Largest Group\n")
    words1 = ["eat", "tea", "tan", "ate", "nat", "bat"]
    print("analyze_anagrams:", analyze_anagrams(words1))
    print("all groups:", get_all_anagram_groups(words1))

    words2 = ["abc", "bca", "cab", "xyz", "zyx", "def"]
    print("analyze_anagrams:", analyze_anagrams(words2))
    print("all groups:", get_all_anagram_groups(words2))

    words3 = ["a", "aa", "aaa"]
    print("analyze_anagrams:", analyze_anagrams(words3))
    print("all groups:", get_all_anagram_groups(words3))

    words4 = ["Ab", "bA", "abc", "bca", "XYZ", "zyx"]
    print("analyze_anagrams:", analyze_anagrams(words4))
    print("all groups:", get_all_anagram_groups(words4))

    words5 = ["listen", "silent", "hello", "bored", "robed", "study", "dusty", "THE", "HET"]
    print("analyze_anagrams:", analyze_anagrams(words5))
    print("all groups:", get_all_anagram_groups(words5)) 