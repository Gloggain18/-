using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Windows.Forms;

namespace QuizApp
{
    public partial class QuizForm : Form
    {
        private List<Question> questions;
        private int currentQuestionIndex = 0;
        private int score = 0;

        public QuizForm()
        {
            InitializeComponent();
            LoadQuestions("questions.txt");
            ShowQuestion();
        }

        private void LoadQuestions(string filePath)
        {
            questions = new List<Question>();
            if (File.Exists(filePath))
            {
                var lines = File.ReadAllLines(filePath);
                for (int i = 0; i < lines.Length; i += 5)
                {
                    var question = new Question
                    {
                        Text = lines[i],
                        Options = lines.Skip(i + 1).Take(3).ToArray(),
                        CorrectAnswer = lines[i + 4]
                    };
                    questions.Add(question);
                }
                var rnd = new Random();
                questions = questions.OrderBy(q => rnd.Next()).ToList();
            }
            else
            {
                MessageBox.Show("Файл питань не знайдено.", "Помилка", MessageBoxButtons.OK, MessageBoxIcon.Error);
                Close();
            }
        }

        private void ShowQuestion()
        {
            if (currentQuestionIndex < questions.Count)
            {
                var q = questions[currentQuestionIndex];
                lblQuestion.Text = q.Text;
                radioButton1.Text = q.Options[0];
                radioButton2.Text = q.Options[1];
                radioButton3.Text = q.Options[2];
                radioButton1.Checked = radioButton2.Checked = radioButton3.Checked = false;
            }
            else
            {
                MessageBox.Show($"Вікторина завершена! Ваш результат: {score}/{questions.Count}", "Результат", MessageBoxButtons.OK, MessageBoxIcon.Information);
                if (MessageBox.Show("Бажаєте пройти ще раз?", "Перезапуск", MessageBoxButtons.YesNo) == DialogResult.Yes)
                {
                    RestartQuiz();
                }
                else
                {
                    Close();
                }
            }
        }

        private void btnNext_Click(object sender, EventArgs e)
        {
            if (!radioButton1.Checked && !radioButton2.Checked && !radioButton3.Checked)
            {
                MessageBox.Show("Будь ласка, виберіть відповідь!", "Увага", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            var selectedAnswer = radioButton1.Checked ? radioButton1.Text : radioButton2.Checked ? radioButton2.Text : radioButton3.Text;
            if (selectedAnswer == questions[currentQuestionIndex].CorrectAnswer)
                score++;

            currentQuestionIndex++;
            ShowQuestion();
        }

        private void RestartQuiz()
        {
            currentQuestionIndex = 0;
            score = 0;
            var rnd = new Random();
            questions = questions.OrderBy(q => rnd.Next()).ToList();
            ShowQuestion();
        }
    }

    public class Question
    {
        public string Text { get; set; }
        public string[] Options { get; set; }
        public string CorrectAnswer { get; set; }
    }
}

