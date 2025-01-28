from datetime import datetime, timedelta

# Напоминания: с 1 по 5
class Reminder:
    FIRST_REMINDER = '20 минут'
    SECOND_REMINDER = '3 часа'
    THIRD_REMINDER = '1 день'
    FOURTH_REMINDER = '3 дня'
    FIFTH_REMINDER = '1 неделя'
    SIXTH_REMINDER = '3 недели'
    SEVENTH_REMINDER = '1,5 месяца'

class ReminderScheduler:
    def __init__(self, bot, scheduler):
        self.bot = bot
        self.scheduler = scheduler

    def schedule_reminders(self, chat_id, word_id, target_word, translate_word):
        intervals = [
            20 * 60,  # 20 минут
            3 * 60 * 60,  # 3 часа
            24 * 60 * 60,  # 1 день
            3 * 24 * 60 * 60,  # 3 дня
            7 * 24 * 60 * 60,  # 1 неделя
            21 * 24 * 60 * 60,  # 3 недели
            45 * 24 * 60 * 60  # 1,5 месяца
        ]

        now = datetime.now()

        for i, interval in enumerate(intervals):
            run_date = now + timedelta(seconds=interval)
            self.scheduler.add_job(
                self.send_reminder,
                'date',
                run_date=run_date,
                args=[chat_id, word_id, target_word, translate_word, i+1]
            )

    def send_reminder(self, chat_id, word_id, target_word, translate_word, attempt):
        self.bot.send_message(chat_id, f"🕒 Напоминание #{attempt}:\n"
                                       f"\n{target_word} - {translate_word}")

    def cancel_reminder(self, word_id):
        jobs = self.scheduler.get_jobs()
        for job in jobs:
            if job.args[1] == word_id:
                self.scheduler.remove_job(job.id)