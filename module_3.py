# -*- coding: utf-8 -*-
"""
Created on Sun Sep 27 22:09:28 2026

@author: Raginikalode
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional


class Transaction:
    """Encapsulates an immutable record of an account transaction."""

    def __init__(self, tx_type: str, amount: float, balance_after: float):
        self._timestamp: datetime = datetime.now()
        self._tx_type: str = tx_type
        self._amount: float = amount
        self._balance_after: float = balance_after

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def tx_type(self) -> str:
        return self._tx_type

    @tx_type.setter
    def tx_type(self, value: str) -> None:
        self._tx_type = value

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def balance_after(self) -> float:
        return self._balance_after

    def __str__(self) -> str:
        return (
            f"[{self._timestamp.strftime('%Y-%m-%d %H:%M:%S')}] "
            f"{self._tx_type:<22} | Amount: ${self._amount:>9,.2f} | "
            f"Balance: ${self._balance_after:>9,.2f}"
        )


class Account(ABC):
    """Abstract Base Class providing the common interface and state for all account types."""

    def __init__(self, account_number: str, holder_name: str, initial_deposit: float = 0.0):
        if initial_deposit < 0:
            raise ValueError("Initial deposit cannot be negative.")
        self._account_number: str = account_number
        self._holder_name: str = holder_name
        self._balance: float = initial_deposit
        self._transactions: List[Transaction] = []

        if initial_deposit > 0:
            self._record_transaction("Account Opened", initial_deposit)

    @property
    def account_number(self) -> str:
        return self._account_number

    @property
    def holder_name(self) -> str:
        return self._holder_name

    @property
    def balance(self) -> float:
        return self._balance

    def _record_transaction(self, tx_type: str, amount: float) -> None:
        """Internal helper to log every balance-altering event."""
        self._transactions.append(Transaction(tx_type, amount, self._balance))

    def deposit(self, amount: float) -> bool:
        """Adds money to the account and logs the event."""
        if amount <= 0:
            print(f"[{self._account_number}] Deposit failed: Amount must be greater than zero.")
            return False

        self._balance += amount
        self._record_transaction("Deposit", amount)
        print(f"[{self._account_number}] Deposited ${amount:,.2f}. New balance: ${self._balance:,.2f}")
        return True

    @abstractmethod
    def withdraw(self, amount: float) -> bool:
        """Deducts money based on account-specific rules."""
        pass

    def get_statement(self) -> List[str]:
        """Returns string representations of all recorded transactions."""
        return [str(tx) for tx in self._transactions]

    def display_statement(self) -> None:
        """Prints a ledger statement for the account."""
        print(f"\n{'=' * 70}")
        print(f"STATEMENT FOR ACCOUNT: {self._account_number} ({self._holder_name})")
        print(f"{'=' * 70}")
        if not self._transactions:
            print("No transactions recorded.")
        else:
            for entry in self.get_statement():
                print(entry)
        print(f"{'-' * 70}")
        print(f"CURRENT BALANCE: ${self._balance:,.2f}")
        print(f"{'=' * 70}\n")


class SavingsAccount(Account):
    """Account type requiring a minimum balance and earning periodic interest."""

    def __init__(
        self,
        account_number: str,
        holder_name: str,
        initial_deposit: float = 0.0,
        min_balance: float = 100.0,
        interest_rate: float = 0.04,
    ):
        super().__init__(account_number, holder_name, initial_deposit)
        self._min_balance: float = min_balance
        self._interest_rate: float = interest_rate

    @property
    def min_balance(self) -> float:
        return self._min_balance

    @property
    def interest_rate(self) -> float:
        return self._interest_rate

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            print(f"[{self.account_number}] Withdrawal rejected: Amount must be greater than zero.")
            return False

        if self._balance - amount < self._min_balance:
            print(
                f"[{self.account_number}] Withdrawal rejected: Must maintain minimum balance "
                f"of ${self._min_balance:,.2f}. Current balance: ${self._balance:,.2f}"
            )
            return False

        self._balance -= amount
        self._record_transaction("Withdrawal", amount)
        print(f"[{self.account_number}] Withdrew ${amount:,.2f}. New balance: ${self._balance:,.2f}")
        return True

    def apply_interest(self) -> None:
        """Calculates and credits interest earned on the balance."""
        interest = self._balance * self._interest_rate
        self._balance += interest
        self._record_transaction(f"Interest (+{self._interest_rate * 100:.1f}%)", interest)
        print(f"[{self.account_number}] Credited interest: ${interest:,.2f}. New balance: ${self._balance:,.2f}")


class CheckingAccount(Account):
    """Account type with overdraft protection up to an authorized credit limit."""

    def __init__(
        self,
        account_number: str,
        holder_name: str,
        initial_deposit: float = 0.0,
        overdraft_limit: float = 500.0,
    ):
        super().__init__(account_number, holder_name, initial_deposit)
        self._overdraft_limit: float = overdraft_limit

    @property
    def overdraft_limit(self) -> float:
        return self._overdraft_limit

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            print(f"[{self.account_number}] Withdrawal rejected: Amount must be greater than zero.")
            return False

        max_withdrawal = self._balance + self._overdraft_limit
        if amount > max_withdrawal:
            print(
                f"[{self.account_number}] Withdrawal rejected: Overdraft limit exceeded. "
                f"Max permitted: ${max_withdrawal:,.2f}"
            )
            return False

        self._balance -= amount
        self._record_transaction("Withdrawal", amount)
        print(f"[{self.account_number}] Withdrew ${amount:,.2f}. New balance: ${self._balance:,.2f}")
        return True


class Bank:
    """Manages the lifecycle of accounts and handles fund transfers."""

    def __init__(self, name: str):
        self.name: str = name
        self._accounts: Dict[str, Account] = {}

    def register_account(self, account: Account) -> None:
        if account.account_number in self._accounts:
            raise ValueError(f"Account number '{account.account_number}' already exists in system.")
        self._accounts[account.account_number] = account
        print(f"[{self.name}] Registered account {account.account_number} for {account.holder_name}.")

    def get_account(self, account_number: str) -> Optional[Account]:
        return self._accounts.get(account_number)

    def transfer(self, sender_acc_num: str, receiver_acc_num: str, amount: float) -> bool:
        """Executes a transfer between two existing accounts."""
        sender = self.get_account(sender_acc_num)
        receiver = self.get_account(receiver_acc_num)

        if not sender:
            print(f"Transfer failed: Sender '{sender_acc_num}' not found.")
            return False
        if not receiver:
            print(f"Transfer failed: Receiver '{receiver_acc_num}' not found.")
            return False
        if sender_acc_num == receiver_acc_num:
            print("Transfer failed: Cannot transfer money to the same account.")
            return False

        # Polymorphic withdrawal checks sender's specific account restrictions
        if sender.withdraw(amount):
            receiver.deposit(amount)
            # Tag the ledger entries with contextual transfer details
            sender._transactions[-1].tx_type = f"Transfer -> {receiver_acc_num}"
            receiver._transactions[-1].tx_type = f"Transfer <- {sender_acc_num}"
            print(f"Success: Transferred ${amount:,.2f} from {sender_acc_num} to {receiver_acc_num}.")
            return True

        print(f"Transfer failed: {sender_acc_num} could not fulfill the withdrawal.")
        return False


# =====================================================================
# SYSTEM VERIFICATION / RUNNABLE DEMO
# =====================================================================
if __name__ == "__main__":
    print("--- 1. INITIALIZING BANK & ACCOUNTS ---")
    bank = Bank("Apex Global Bank")

    # Creating polymorphic accounts
    savings = SavingsAccount(
        account_number="SA-101",
        holder_name="Alice Smith",
        initial_deposit=1000.0,
        min_balance=200.0,
        interest_rate=0.05,
    )
    checking = CheckingAccount(
        account_number="CA-202",
        holder_name="Bob Jones",
        initial_deposit=400.0,
        overdraft_limit=500.0,
    )

    bank.register_account(savings)
    bank.register_account(checking)

    print("\n--- 2. ENCAPSULATION & BUSINESS LOGIC CHECKS ---")
    # Valid deposit
    savings.deposit(500.0)

    # Denied withdrawal: Violates SavingsAccount minimum balance ($1500 - $1400 = $100 < $200 min)
    savings.withdraw(1400.0)

    # Allowed overdraft: CheckingAccount dips into overdraft ($400 - $600 = -$200)
    checking.withdraw(600.0)

    # Denied overdraft: Exceeds the $500 overdraft limit (-$200 - $400 = -$600)
    checking.withdraw(400.0)

    print("\n--- 3. POLYMORPHIC PROCESSING & INTEREST ---")
    # Polymorphism: Both SavingsAccount and CheckingAccount respond to Account methods
    all_accounts: List[Account] = [savings, checking]
    for acc in all_accounts:
        print(f"Auditing Account {acc.account_number}: Current Balance = ${acc.balance:,.2f}")

    savings.apply_interest()

    print("\n--- 4. INTER-ACCOUNT TRANSFER ---")
    # Alice transfers $300 to Bob
    bank.transfer(sender_acc_num="SA-101", receiver_acc_num="CA-202", amount=300.0)

    print("\n--- 5. LEDGER & AUDIT STATEMENTS ---")
    savings.display_statement()
    checking.display_statement()