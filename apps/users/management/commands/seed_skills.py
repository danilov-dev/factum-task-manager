# apps/users/management/commands/seed_skills.py
from django.core.management.base import BaseCommand
from apps.users.models import Skill


class Command(BaseCommand):
    help = 'Наполняет базу данных начальным списком навыков по категориям'

    # Словарь: Категория -> Список навыков
    SKILLS_DATA = {
        Skill.Category.IT_DEV: [
            'Python',
            'Django',
            'Flask',
            'FastAPI',
            'JavaScript',
            'TypeScript',
            'React',
            'Vue.js',
            'Angular',
            'HTML5',
            'CSS3',
            'Tailwind CSS',
            'Bootstrap',
            'PostgreSQL',
            'MySQL',
            'MongoDB',
            'Redis',
            'Git',
            'GitHub/GitLab',
            'Docker',
            'Kubernetes',
            'CI/CD (Jenkins, GitHub Actions)',
            'Настройка серверов (Linux, Nginx)',
            'AWS / Yandex Cloud',
            'REST API разработка',
            'GraphQL',
            'WebSockets',
            'Очереди (Celery, Redis)',
            'Тестирование (Pytest, Unittest)',
            'Безопасность веб-приложений'
        ],

        Skill.Category.DESIGN: [
            'Figma',
            'Adobe Photoshop',
            'Adobe Illustrator',
            'Adobe InDesign',
            'Adobe After Effects',
            'Adobe Premiere Pro',
            'Sketch',
            'UI/UX Дизайн',
            'Веб-дизайн',
            'Мобильный дизайн (iOS/Android)',
            'Создание логотипов и айдентики',
            'Брендинг',
            'Типографика',
            'Композиция и цветокоррекция',
            '3D-моделирование (Blender)',
            '3D-моделирование (Cinema 4D)',
            'Прототипирование интерактивных интерфейсов',
            'Дизайн презентаций',
            'Полиграфический дизайн',
            'Ретушь и обработка фото',
            'Инфографика',
            'Векторная графика',
            'Motion-дизайн',
            'Скетчинг и иллюстрация'
        ],

        Skill.Category.MARKETING: [
            'SMM (ВКонтакте, Telegram, Instagram)',
            'Таргетированная реклама (VK, FB, TG)',
            'Контекстная реклама (Яндекс.Директ, Google Ads)',
            'SEO-оптимизация',
            'Контент-маркетинг',
            'E-mail маркетинг',
            'PR и работа со СМИ',
            'Организация коллабораций',
            'Медиапланирование',
            'Аналитика (Яндекс.Метрика, Google Analytics)',
            'A/B тестирование',
            'Копирайтинг',
            'Сторителлинг',
            'Разработка контент-стратегии',
            'Community-менеджмент',
            'Бренд-менеджмент',
            'Маркетинговые исследования',
            'Репортажная съёмка для соцсетей',
            'Чат-боты и автоматизация',
            'Личный бренд',
            'Партнерский маркетинг',
            'Видео-маркетинг',
            'Подкастинг'
        ],

        Skill.Category.MANAGEMENT: [
            'Управление проектами (Project Management)',
            'Методологии Agile/Scrum',
            'Канбан',
            'Управление продуктом (Product Management)',
            'Организация мероприятий (Event-менеджмент)',
            'Фасилитация встреч',
            'Ведение переговоров',
            'Деловая переписка',
            'Тайм-менеджмент',
            'Командообразование',
            'Мотивация сотрудников',
            'Оценка эффективности (KPI)',
            'Бюджетирование проектов',
            'Риск-менеджмент',
            'CRM-системы (Bitrix, AmoCRM)',
            'HR-менеджмент',
            'Управление изменениями',
            'Коучинг',
            'Наставничество',
            'Кризисный менеджмент',
            'Стратегическое планирование',
            'Форсайт и прогнозирование',
            'Межкультурная коммуникация'
        ],

        Skill.Category.FINANCE: [
            'Написание грантовых заявок',
            'Фандрайзинг и поиск спонсоров',
            'Краудфандинг (Planeta, Boomstarter)',
            'Бухгалтерский учет для НКО',
            'Финансовое планирование',
            'Бюджетирование',
            'Финансовая отчетность',
            'Инвестиционный анализ',
            'Юридическое сопровождение НКО',
            'Налоговое планирование',
            'Работа с донорами',
            'Составление отчетов для грантодателей',
            'Аудит',
            'Управление оборотным капиталом',
            'Финансовые модели',
            'Оценка рисков',
            'Работа с банками и платежными системами',
            'Благотворительные программы',
            'Социальное предпринимательство',
            'Бизнес-планирование',
            'Презентация проектов инвесторам',
            'Документооборот НКО'
        ],

        Skill.Category.EDUCATION: [
            'Преподавание и проведение тренингов',
            'Менторство',
            'Разработка учебных программ',
            'Психологическая поддержка',
            'Коучинг',
            'Онлайн-преподавание',
            'Создание образовательных курсов',
            'Геймификация в обучении',
            'Оценка результатов обучения',
            'Работа с разными возрастными группами',
            'Интерактивные методы обучения',
            'Публичные выступления',
            'Ораторское искусство',
            'Навыки модерации дискуссий',
            'Дебаты и аргументация',
            'Конфликтология',
            'Эмоциональный интеллект',
            'Развитие критического мышления',
            'Профориентация',
            'Адаптация учебных материалов',
            'Создание инфографики для образования',
            'Игровые методики (EdTech)',
            'Обучение людей с ОВЗ',
            'Волонтерство в образовании'
        ],

        Skill.Category.OTHER: [
            'Фотография',
            'Видеосъемка и монтаж',
            'Аэросъемка (дроны)',
            'Монтаж видео (Premiere, Final Cut)',
            'Звукорежиссура',
            'Юридическая консультация',
            'Работа с договорами',
            'Волонтёрство на площадке (логистика)',
            'Работа с текстовыми редакторами',
            'Перевод (английский)',
            'Перевод (китайский)',
            'Перевод (испанский)',
            'Перевод (французский)',
            'Жестовый язык',
            'Спортивный судья',
            'Организация спортивных мероприятий',
            'Экологическое волонтерство',
            'Уход за животными',
            'Садоводство и ландшафтный дизайн',
            'Кулинария и кейтеринг',
            'Игротехника',
            'Анимация и работа с детьми',
            'Каллиграфия',
            'Рукоделие и народные промыслы',
            'Музыкальные инструменты',
            'Вокал',
            'Хореография'
        ]
    }

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('🚀 Начинаю наполнение базы данных навыками...'))
        self.stdout.write('=' * 60)

        created_count = 0
        skipped_count = 0
        category_stats = {}

        for category, skills_list in self.SKILLS_DATA.items():
            category_created = 0
            category_skipped = 0

            self.stdout.write(f'\n📂 Категория: {category}')
            self.stdout.write(f'   Навыков в списке: {len(skills_list)}')

            for skill_name in skills_list:
                obj, created = Skill.objects.get_or_create(
                    name=skill_name,
                    defaults={'category': category}
                )

                if created:
                    created_count += 1
                    category_created += 1
                else:
                    skipped_count += 1
                    category_skipped += 1

            category_stats[category] = {
                'created': category_created,
                'skipped': category_skipped,
                'total': len(skills_list)
            }

            self.stdout.write(self.style.SUCCESS(
                f'   ✅ Добавлено: {category_created}, пропущено: {category_skipped}'
            ))

        # Итоговая статистика
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('📊 ИТОГОВАЯ СТАТИСТИКА:'))
        self.stdout.write('-' * 60)

        total_skills = sum(len(skills) for skills in self.SKILLS_DATA.values())

        for category, stats in category_stats.items():
            self.stdout.write(
                f'{category}: {stats["total"]} навыков '
                f'(добавлено: {stats["created"]}, существовало: {stats["skipped"]})'
            )

        self.stdout.write('-' * 60)
        self.stdout.write(self.style.SUCCESS(
            f'✅ ВСЕГО: {total_skills} навыков в {len(self.SKILLS_DATA)} категориях'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'✨ Добавлено новых: {created_count}, пропущено (уже есть): {skipped_count}'
        ))
        self.stdout.write(self.style.SUCCESS('🎉 База данных навыков успешно заполнена!'))