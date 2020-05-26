def create_file_with_size(path, byte_size):
    with open(path, "wb") as file:
        # sparse file that doesn't actually take up that amount of space on disk
        multiplier = int(round(byte_size))
        file.write(b"\0" * multiplier)


def compare_nested_array_content_ignoring_order(array_a, array_b):
    """Works for arrays that can be sorted"""
    array_a_sorted_inner = map(lambda element: sorted(element), array_a)
    array_b_sorted_inner = map(lambda element: sorted(element), array_b)

    return sorted(array_a_sorted_inner) == sorted(array_b_sorted_inner)
