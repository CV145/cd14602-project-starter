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
- QuizMode: 


## Acceptance Criteria 


## Out of Scope 


## Mermaid Diagram