from tacotron.utils.text import text_to_sequence, sequence_to_text

# file_name = "metadata_0911_without_period.csv"
file_name = "label_all_7_final.txt"

with open(file_name, encoding="utf-8") as f:
	while 1:
		line = f.readline()
		if not line:
			break
		name, text = line.split("|")

		seq = text_to_sequence(text, ["basic_cleaners"])
		text_edit = sequence_to_text(seq)
		print(text.strip())
		print(text_edit)
