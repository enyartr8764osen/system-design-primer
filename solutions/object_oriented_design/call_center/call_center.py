#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Call center object oriented design solution.

Implements a call center with employees at three levels:
  - Respondent (entry level)
  - Manager
  - Director

Incoming calls are first routed to available respondents.
If none are free, the call escalates to managers, then directors.
"""

from collections import deque
from enum import Enum


class Rank(Enum):
    RESPONDENT = 0
    MANAGER = 1
    DIRECTOR = 2


class Call:
    """Represents an incoming call."""

    def __init__(self, caller_id: str):
        self.caller_id = caller_id
        self.rank = Rank.RESPONDENT
        self.handler = None

    def __repr__(self):
        return f"Call(caller={self.caller_id}, rank={self.rank.name})"


class Employee:
    """Base class for all call center employees."""

    def __init__(self, name: str, rank: Rank, call_center):
        self.name = name
        self.rank = rank
        self.call_center = call_center
        self.current_call: Call | None = None

    @property
    def is_free(self) -> bool:
        return self.current_call is None

    def take_call(self, call: Call):
        """Assign a call to this employee."""
        if not self.is_free:
            raise RuntimeError(f"{self.name} is already on a call.")
        self.current_call = call
        call.handler = self
        print(f"{self.rank.name} {self.name} picked up {call}")

    def finish_call(self):
        """Mark the current call as finished and notify the call center."""
        if self.current_call is None:
            return
        print(f"{self.rank.name} {self.name} finished {self.current_call}")
        self.current_call = None
        self.call_center.notify_free(self)

    def escalate_call(self):
        """Escalate the current call to the next rank."""
        if self.current_call is None:
            return
        call = self.current_call
        self.current_call = None
        call.rank = Rank(self.rank.value + 1)
        print(f"{self.rank.name} {self.name} escalated {call}")
        self.call_center.dispatch_call(call)


class Respondent(Employee):
    def __init__(self, name: str, call_center):
        super().__init__(name, Rank.RESPONDENT, call_center)


class Manager(Employee):
    def __init__(self, name: str, call_center):
        super().__init__(name, Rank.MANAGER, call_center)


class Director(Employee):
    def __init__(self, name: str, call_center):
        super().__init__(name, Rank.DIRECTOR, call_center)


class CallCenter:
    """Manages employees and routes incoming calls."""

    def __init__(self):
        self.employees: dict[Rank, list[Employee]] = {
            Rank.RESPONDENT: [],
            Rank.MANAGER: [],
            Rank.DIRECTOR: [],
        }
        self.call_queue: deque[Call] = deque()

    def add_employee(self, employee: Employee):
        self.employees[employee.rank].append(employee)

    def _find_free_employee(self, rank: Rank) -> Employee | None:
        for emp in self.employees[rank]:
            if emp.is_free:
                return emp
        return None

    def dispatch_call(self, call: Call):
        """Route a call to the first available employee at the required rank."""
        for rank in list(Rank)[call.rank.value:]:
            emp = self._find_free_employee(rank)
            if emp:
                emp.take_call(call)
                return
        print(f"No available employee for {call}. Queuing call.")
        self.call_queue.append(call)

    def notify_free(self, employee: Employee):
        """Called when an employee finishes a call; dispatch queued calls."""
        if self.call_queue:
            call = self.call_queue.popleft()
            employee.take_call(call)


if __name__ == "__main__":
    center = CallCenter()
    center.add_employee(Respondent("Alice", center))
    center.add_employee(Respondent("Bob", center))
    center.add_employee(Manager("Carol", center))
    center.add_employee(Director("Dave", center))

    calls = [Call(f"customer_{i}") for i in range(4)]
    for c in calls:
        center.dispatch_call(c)
