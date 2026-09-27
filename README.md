Core Architecture & Flow
Transaction (Data Audit): Acts as a read-only record. Every time money moves, it captures a timestamp, transaction type (Deposit, Withdrawal, Transfer), amount, and the resulting balance.

Account (Abstract Base Class): Enforces a blueprint for all accounts. It manages shared fields (_balance, _transactions, account_number) and common methods like deposit() and display_statement(). It marks withdraw() as an @abstractmethod, forcing child classes to implement their own rules.

SavingsAccount (Inheritance & Validation): Inherits from Account. Overrides withdraw() to ensure the balance never dips below a required threshold (min_balance = $100). Adds apply_interest() to calculate and credit earnings.

CheckingAccount (Overdraft Protection): Inherits from Account. Overrides withdraw() to permit negative balances down to an authorized credit limit (overdraft_limit = $500).

Bank (System Coordinator): Stores registered accounts in a dictionary (_accounts). It handles lookups and manages the transfer() method—atomically withdrawing from the sender and depositing into the receiver only if the sender's withdrawal conditions pass.
