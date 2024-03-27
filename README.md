# virtual-football-td


## TUPLES
This repository is created as part of the [TUPLES Project](https://tuples.ai/).
This project has received funding from the European Union’s HORIZON-CL4-2021-HUMAN-01 research and innovation programme 
under grant agreement No. 101070149

TUPLES is about building trustworthy planning and scheduling systems using AI. Multiple academic partners will answer
related research questions and implement new technology on various industry use-cases, of which the use-case
presented in this repository is one.

## Purpose
The purpose of this repository is to provide a simplified and semi-realistic example of the squad management use-case,
showcasing various uncertainty, robustness and modelling properties that need solving in scope of the TUPLES project.

Most data and models used in scope of TUPLES are sensitive or proprietary and can thus not be made openly available.
Therefore, the purpose of this repository is to allow the user to simulate the use-case and its properties using
randomly generated synthetic data.

## Usage-Guide

### Squad management simulator
In the “virtualtd” simulator, the user takes the role of a technical director (TD) 
that manages a professional football team. 
The goal of the user is to optimize the team’s performance and development over the course of multiple 
competition seasons, fulfilling one or multiple of the following goals:
- Maximize the performance of the team in terms of points achieved and competitive ranking. 
- Maximize the development of the team in terms of the skill level of its players and estimated transfer value (ETV). 
- Maximize the financial profit of the team through selling and buying players without violating the constraints 
- for minimal performance levels. 

As a “virtual technical director” the user is in charge of a squad of 
33 players (22 first-team players + 11 academy players), and has to make certain planning decisions 
to fulfill the goals:
1. How to distribute the minutes across players;
2. What players to buy and what players to sell;
3. What contracts to extend and when. 

Every decision made by the user will impact the expected team performance level (expected points and ranking) 
development of certain or all players, and by extension the financial situation of the team. 
The user is free to make decisions as they choose, but cannot certain financial and performance constraints. 

### Simulator Data
The simulator provides a simplified situation that is exemplary for the squad management use-case, 
and only contains synthetic data. The simulator repository contains various options to generate synthetic data, 
either randomly, user-specified or by choosing from a set of pre-configured scenarios.

### Capitalization
The open-access simulator allows users to conceptualize squad management solutions that optimize the same goals, 
and manipulate the same decisions, as are set in scope of SciSports’ contribution to TUPLES, 
albeit in a simplified manner with synthetic data and a lower granularity. 

## User-Instruction

To simulate a squad management use-case and step in the role of a virtual director, the user needs to follow the
subsequent steps:

First, initialize the simulation:
1. Generate a league of n teams with `from virtualtd.generators.creator.LeagueGenerator`;
2. Generate a transfermarkt of n players with `from virtualtd.generators.creator.TransferMarktGenerator`;

Next, simulate the league and decisions of the virtual-td by running the following iteration n-times:
1. Simulate the first half of the season;
2. Simulate the transfer window in the winter-break;
3. Mutate the squad;
4. Simulate the second half of the season;
5. Simulate the transfer window in the summer-break;
6. Mutate the squad;
7. Start a new season. 

For an MVP example see `virtualtd.interface.mvp`

## SciSports
Founded in 2013, SciSports is one of the fastest growing sports analytics companies in the world and a leading provider 
of football data intelligence to over 100 professional football organisations worldwide ranging from clubs, leagues, 
federations, agencies and media & entertainment companies. Our industry-leading product suite enables sports 
professionals to make better-informed decisions and achieve their goals in scouting and performance analysis 
every single day. The SciSports team consists of specialists in artificial intelligence, 
data analytics and data scouting.

See [website](https://www.scisports.com/) for more info.

### Use-Case Description
The main objective of football clubs is twofold: 
having success on the pitch and making money over time by selling players, match tickets, and more. 
Clubs’ technical directors are responsible for selling and buying players and thus need to plan how their squad will 
evolve over the coming years. 
The task that we try to solve in this use case is to optimally spend the available budget on buying new players 
while optimizing specified objectives on and off the pitch

From a technical perspective, developing such an approach would require the following four key capabilities:
The ability to learn the predictive models that capture the uncertainty about the future 
(e.g, how a player will evolve over time)
A planner that can integrate and interact with the predictive models to plan player acquisitions
Approaches to verify robustness properties of the outcomes – both for the predictive models and the planner
The ability to explain the outputs of both the predictive models and the overall plan itself

#### Uncertainties
There are multiple uncertainties in this task as the squad is constantly evolving due to players leaving 
(players sold, players retiring, players temporarily unavailable due to injuries or suspensions) and 
evolving (younger players improve, older players might lose speed but improve their decision making). 
In particular, we need to answer the following questions:

- How do a given player’s qualities evolve over time?
- How will a player’s transfer value evolve over time?
- Given a squad and all opponent squads, what will be our chances of reaching our on-pitch target 
- (e.g. become champion, qualify for Champions League, no relegation)?

#### Robustness
It will be crucial that the Squad Builder will not respond dramatically to irrelevant changes in the input 
or small fluctuations in the environment, like players playing one good match, picking up a minor injury or 
simply time passing by. It is preferable that the Squad Builder comes to similar conclusions during a day and won’t 
change its advice drastically if irrelevant things change. Scouts and technical directors will lose their trust in the 
solution if it turns out not to be robust and it changes its advice constantly.

#### Hybrid Modelling
Interactive explanations will be important to elucidate which types of players should and should not be considered 
as transfer targets and why this is the case. The ability to explain the system’s reasoning will help scouts 
have more trust in its output.


## Disclaimer
ALL DATA GENERATED IN THE SCOPE OF THIS REPOSITORY IS COMPLETELY SYNTHETIC AND BEARS NO RESEMBLANCE TO
ANY REAL-WORLD TEAMS, LEAGUES OR PERSONS. AS THE DATA AND MODELS USED IN SCOPE OF THE USE-CASE RESEARCH FOR TUPLES
IS SENSITIVE, IT CAN NOT BE MADE AVAILABLE TO THE GENERAL PUBLIC, AND AS SUCH WE CHOOSE TO PUBLICLY RELEASE A 
SIMPLIFIED TOY EXAMPLE OF OUR USE-CASE THAT WILL SERVE AS A DEMONSTRATION OF PROTOTYPE SOLUTIONS.

THEREFORE, PLEASE NOTE THAT THE SIMULATIONS HERE ARE A SIMPLIFIED VERSION OF REALITY, AND MIGHT RESULT IN UNREALISTIC
SCENARIOS UPON MANIPULATION OF THE PARAMETERS. THE REPOSITORY MERELY SERVES A DEMONSTRATION & EXPERIMENTATION PURPOSE. 
THE ACADEMIC PARTNERS USE REAL-DATA AND PROPRIETARY MODELS FROM SCISPORTS TO STUDY THIS USE-CASE IN SCOPE OF TUPLES.