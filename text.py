def transform_into_multi_line(text: str, max_chars_in_line: int):
    list_of_words = text.split(' ')
    current_amount_of_chars = 0
    new_list = []
    for word in list_of_words:
        if len(word) + current_amount_of_chars + 1 > max_chars_in_line:
            word = '\n' + word
            current_amount_of_chars = 0
            new_list.append(word)
        else:
            current_amount_of_chars += len(word) + 1
            new_list.append(word)
    return ' '.join(new_list)


text = 'tal is a goat'
t = transform_into_multi_line(text, 5)
print(t)