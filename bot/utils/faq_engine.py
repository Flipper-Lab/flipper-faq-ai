import json
import logging
from pathlib import Path

from whoosh import fields, index
from whoosh.qparser import FuzzyTermPlugin, QueryParser

logger = logging.getLogger(__name__)


class FaqFlipperBot:
    def __init__(self, faq_dir: str = "faq", index_dir: str = "faq_index") -> None:
        self.faq = {}
        self.faq_dir = faq_dir
        self.index_dir = index_dir
        self.ix = None

        self.load_faq()
        self.build_index()

    def load_faq(self) -> None:
        """Загрузка FAQ из JSON-файлов включая подпапки с обработкой ошибок"""
        faq_path = Path(self.faq_dir)
        logger.info(f"Загрузка FAQ из {self.faq_dir}...")
        error_files = []

        for file_path in faq_path.rglob("*.json"):
            category = str(file_path.relative_to(faq_path).with_suffix(""))

            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)

                if "questions" not in data or "answer" not in data:
                    raise ValueError("Некорректная структура файла")

                self.faq[category] = {
                    "questions": data["questions"],
                    "answer": data["answer"],
                }
                logger.info(
                    f"Загружено: {category} ({len(data['questions'])} вопросов)"
                )

            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Ошибка в файле {file_path}: {str(e)}")
                error_files.append(str(file_path))
            except Exception as e:
                logger.error(f"Неизвестная ошибка в {file_path}: {str(e)}")
                error_files.append(str(file_path))

        logger.info(f"Всего загружено: {len(self.faq)} файлов из {self.faq_dir}")
        if error_files:
            logger.warning(
                f"Файлы с ошибками ({len(error_files)}): {', '.join(error_files)}"
            )

    def build_index(self) -> None:
        """Создает или обновляет индекс Whoosh"""
        schema = fields.Schema(
            question=fields.TEXT(stored=True), answer=fields.TEXT(stored=True)
        )

        index_path = Path(self.index_dir)
        if not index_path.exists():
            index_path.mkdir(parents=True)

        self.ix = index.create_in(str(index_path), schema)
        writer = self.ix.writer()

        doc_count = 0
        for _category, data in self.faq.items():
            answer_text = data["answer"]
            for q in data["questions"]:
                writer.add_document(question=q, answer=answer_text)
                doc_count += 1

        writer.commit()
        logger.info(f"Индекс Whoosh построен. Проиндексировано документов: {doc_count}")

    def find_best_matches(self, question: str, limit: int = 3) -> list[str]:
        """Ищет до `limit` лучших уникальных ответов с поддержкой нечеткого поиска"""
        if self.ix is None:
            logger.error("Индекс не инициализирован")
            return []

        try:
            with self.ix.searcher() as searcher:
                parser = QueryParser("question", self.ix.schema)
                parser.add_plugin(FuzzyTermPlugin())

                fuzzy_query_str = " ".join(
                    [f"{word}~2" for word in question.lower().split()]
                )

                try:
                    parsed_query = parser.parse(fuzzy_query_str)
                except Exception as e:
                    logger.error(f"Ошибка парсинга запроса '{question}': {e}")
                    return []

                results = searcher.search(parsed_query, limit=limit)

                if not results:
                    logger.info(f"Вопрос: '{question}' | Совпадений не найдено")
                    return []

                unique_answers = []
                seen_answers = set()

                for hit in results:
                    ans = hit["answer"]
                    if ans not in seen_answers:
                        unique_answers.append(ans)
                        seen_answers.add(ans)
                        logger.info(
                            f"Вопрос: '{question}' | Совпадение: '{hit['question']}' (Score: {hit.score:.2f})"
                        )

                        if len(unique_answers) == limit:
                            break

                return unique_answers

        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            return []
