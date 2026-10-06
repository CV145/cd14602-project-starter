## Goal 
Implement the quiz engine using the Strategy Pattern.

The Logic: You need three distinct ways to serve questions:
SequentialMode: Order 1, 2, 3...
RandomMode: Shuffled order.
AdaptiveMode: Prioritize cards the user gets wrong.
Implement a QuizMode abstract base class. Then create three classes that inherit from it. Use a Factory Pattern to select the correct mode based on user input."

## Constraints 
We will be using the Strategy design pattern.

The strategy design pattern is defined as a way to encapsulate a family of algorithms and make them interchangable, allowing them to be replaced dynamically. 

There should be a Strategy base class, which decouples the Strategy user from the implementation details of the concrete strategies. The Strategy base class defines the interface for the algorithms and the concrete strategies implement this interface. This allows for algorithms to be interchangeable. 

We will have 3 strategies for serving questions:
1. SequentialMode: Order from 1, 2, 3 one at a time
2. RandomMode: Shuffle the order of the cards randomly
3. AdaptiveMode: Prioritize the cards the user gets wrong/

The Strategy base class will be the QuizMode abstract base class. The three strategy classes inherit from it. 

The Factory design pattern will be used to select the correct mode based on user input. This pattern is a way to create objects without exposing instantiation logic to the client. 

Classes:
- QuizMode: Abstract Strategy base class
- QuizEngine: The class that makes everything work
- QuizModeFactory: Has methods like createSequential(), createRandom(), createAdaptive() to create the different strategies
- SequentialStrategy
- RandomStrategy
- AdaptiveStrategy
- Card: A class for a single card

The card "back" answer will be compared with the "front" using case-insensitive comparison after trimming leading and trailing whitespace.

SequentialStrategy: Show cards from start to finish. At the end, repeat to the beginning. User can quit anytime.

RandomStrategy: Present the cards randomly indefinitely. User can quit anytime.

For AdaptiveStrategy, incorrect cards should be prioritized using Spaced Repetition Algorithm (SRA). We forget what 50-80% what we learn within an hour after studying it. Within 24 hours it drops to around 10-25%. We will implement a "decay function" to determine the time until the next review. We will keep the time scope to 5 min, 10 min, and a 15min for easy testing. So when a user gets a card wrong they rate the card and that card is appended to a queue for 5min, a queue for 10min, and a queue for 15min. This data is saved locally between sessions. A session ends when there are no more cards to review (we start with a big list of cards to review first)

Due to time constraints and testing, the cards should be prioritized in this order to the user under the AdaptiveStrategy: new -> 5min -> 10min -> 15min. 

The engine should assign the card automatically (easy, medium, or difficult) based on failure counts. Easy = got it right. Medium = got it wrong only one time. Difficult = got it wrong twice. So what this means is the user gets two attempts to answer the question.

When a card in the 5min queue is answered correctly the first time it moves down to 15min queue. If it gets a medium rating it goes down one queue to 10min. If it gets a difficult rating it stays in 5min. 

An AdaptiveMode session ends when the user wants, otherwise it goes on forever. Ideally, the cards should "automatically" categorize themselves in between sessions based on the amount of time passed. The time should be able to be adjusted by the user, but the default will be 5, 10, 15min. But the user should have the option to setup a custom time for each queue:
- 30min
- 1 hour
- 24 hours
- 1 week
When a new session starts, it should check local saved data for these constraints and adjust cards to their appropriate queues accordingly.

Adaptive session state will be stored in data/quiz_state.json. It will be keyed by the deck name and front card text. If data/quiz_state.json does not exist, initialize it with an empty state. No need to notify the user. 

---
When a user quits a session, the QuizEngine should track how many times the user has gotten a card right and a card wrong between sessions in quiz_state.json. It should then calculate a "total accuracy" percentage of right / wrong to represent the user's overall knowledge rating and mastery.

- Single-threaded application

## Acceptance Criteria 
- test_quiz_mode_factory: factory returns the correct class object
- test_adaptive_mode_behavior: the adaptive strategy repeats incorrect questions
- We import JSON data from the sample decks glossary.json and python_basics.json using file_handler.py. The QuizEngine should receive these cards as input and store them as cards. It will then present the cards using a selected strategy. This feature is considered 'Done" after each strategy is implemented

## Out of Scope 
- We will not be working on UI in this phase
- We will only implement strategy and factory design patterns for now
