from processor import process_pdf
from config import DEFAULT_SETTINGS
import copy


def main():
    settings = copy.deepcopy(DEFAULT_SETTINGS)

    # TEXT_TO_EXCLUDE = [
    #     "Страна: Латвия",
    #     'Импортер: ООО "КОЛЕСОМАРКЕТ"',
    #     "ИНН 7751316402 / КПП 775101001",
    # ]
    # process_pdf(
    #     input_pdf="pdf_labels_old.pdf",
    #     output_pdf="edited_resized_output.pdf",
    #     exclude_texts=TEXT_TO_EXCLUDE,
    #     settings=settings,
    # )


if __name__ == "__main__":
    main()
