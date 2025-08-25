# How to Use This API Locally

1. Clone the repository:
   ```
   git clone https://github.com/johankaibutsu/gold-investment-api.git
   ```

2. Navigate to the project directory:
   ```
   cd gold-investment-api
   ```

3. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

5. Edit the sample.env to just .env and put your own API key:
   ```
   cp sample.env .env
   # Edit .env file and replace YOUR_API_KEY with your actual API key
   ```

6. Run the application:
   ```
   uvicorn main:app --reload
   ```

7. Access the API at `http://127.0.0.1:8000/docs` You get a nice interface thanks to swagger UI.


# How to test the API Workflow
## Scenario 1: When user asks about gold investment or any other investment options

1. Expand the POST /chat endpoint and click "Try it out".
2. Enter the following in the request body. Let's use user_test_jk as our user.
```JSON
{
  "user_id": "user_test_jk",
  "question": "Why should I consider gold as an investment?"
}
```
3. Click "Execute".
Expected Response: You'll get a standard response from the model that includes the nudge.
```JSON
{
  "llm_answer": "Gold is often considered a safe-haven asset... Would you like to see some digital gold investment options?",
  "action_to_perform": null
}
```
Behind the Scenes: A new row has been added to your chat_history.db with this question and answer for user_test_jk.
4. Change the request body to the following, using the same user_id:
```JSON
{
  "user_id": "user_test_jk",
  "question": "yes sure"
}
```
5. Click "Execute".
Expected Response: This time, the API recognizes the context and provides the action command.
```JSON
{
  "llm_answer": "Great! Here are the investment options available for you.",
  "action_to_perform": "call_investment_options"
}
```
This action will perform the redirect on the frontend.

## Scenario 2: When user asks anything else

1. Expand the POST /chat endpoint and click "Try it out".
2. Enter the following in the request body. Let's use user_test_jk as our user.
```JSON
{
  "user_id": "user_test_jk",
  "question": "What is the best recipe for chocolate cake?"
}
```
3. Click "Execute".
Expected Response: You'll get a standard response from the model that includes the nudge.
```JSON
{
  "llm_answer": "I can't help you with this",
  "action_to_perform": null
}
```
## Redirect API endpoint
Another endpoint is /invest/options which just gives you a hardcoded json response about all the investment options available and some basic information about each option. In a working application after the user has given the confirmation, the API will redirect the user to this investment options page.
```JSON
{
  "options": [
    {
      "plan_name": "Gold Starter Pack",
      "duration_months": 6,
      "min_investment": 500,
      "description": "A perfect plan for beginners."
    },
    {
      "plan_name": "Steady Saver",
      "duration_months": 12,
      "min_investment": 1000,
      "description": "Systematically invest every month for a year."
    },
    {
      "plan_name": "Wealth Builder",
      "duration_months": 24,
      "min_investment": 2500,
      "description": "A long-term plan for serious investors."
    }
  ],
  "purchase_steps": [
    "1. Select a plan.",
    "2. Complete KYC.",
    "3. Make payment.",
    "4. Gold is credited!"
  ]
}
```
