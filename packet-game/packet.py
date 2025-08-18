#!/usr/bin/env python3
"""Packet and Queue management for the Packet Game."""

import random
from typing import List, Optional


class Packet:
    """
    A packet with value and deadline.
    
    Attributes:
        value: Packet value (1-10)
        deadline: Turns until expiration (starts at 5)
        arrival_turn: Turn when packet arrived (for tracking)
    """
    
    def __init__(self, value: int, deadline: int = 5, arrival_turn: int = 0):
        """
        Initialize a packet.
        
        Args:
            value: Packet value (1-10)
            deadline: Initial deadline (default 5)
            arrival_turn: Turn when packet arrived
        """
        self.value = value
        self.deadline = deadline
        self.arrival_turn = arrival_turn
    
    def tick(self):
        """Decrease deadline by 1."""
        self.deadline -= 1
    
    def is_expired(self) -> bool:
        """Check if packet has expired."""
        return self.deadline <= 0
    
    def get_priority(self) -> float:
        """
        Calculate priority score for decision making.
        Higher score = higher priority.
        """
        # Balance value and urgency
        # Urgent packets get higher priority
        if self.deadline == 0:
            return 0  # Expired
        return self.value / self.deadline
    
    def get_urgency_marker(self) -> str:
        """Get visual urgency marker for display."""
        if self.deadline <= 0:
            return " 💀 EXPIRED"
        elif self.deadline == 1:
            return " 🔥 CRITICAL"
        elif self.deadline == 2:
            return " ⚠️ URGENT"
        elif self.deadline == 5:
            return " ✨ NEW"
        return ""
    
    def __repr__(self) -> str:
        """String representation with urgency marker."""
        return f"(v={self.value}, d={self.deadline}){self.get_urgency_marker()}"
    
    def __str__(self) -> str:
        """Simple string representation."""
        return f"(v={self.value}, d={self.deadline})"


class PacketQueue:
    """
    Manages a queue of packets for an agent.
    """
    
    def __init__(self):
        """Initialize empty queue."""
        self.packets: List[Packet] = []
    
    def add_packet(self, packet: Packet):
        """
        Add a packet to the queue.
        
        Args:
            packet: Packet to add
        """
        self.packets.append(packet)
    
    def remove_packet(self, packet: Packet):
        """
        Remove a packet from the queue.
        
        Args:
            packet: Packet to remove
        """
        if packet in self.packets:
            self.packets.remove(packet)
    
    def get_valid_packets(self) -> List[Packet]:
        """
        Get all non-expired packets.
        
        Returns:
            List of valid packets
        """
        return [p for p in self.packets if not p.is_expired()]
    
    def update_deadlines(self):
        """
        Decrease all packet deadlines by 1 and remove expired packets.
        
        Returns:
            List of expired packets (for tracking)
        """
        expired = []
        for packet in self.packets:
            packet.tick()
            if packet.is_expired():
                expired.append(packet)
        
        # Remove expired packets
        for packet in expired:
            self.packets.remove(packet)
        
        return expired
    
    def get_sorted_by_priority(self) -> List[Packet]:
        """
        Get packets sorted by priority (highest first).
        
        Returns:
            Sorted list of valid packets
        """
        valid = self.get_valid_packets()
        return sorted(valid, key=lambda p: p.get_priority(), reverse=True)
    
    def get_sorted_by_deadline(self) -> List[Packet]:
        """
        Get packets sorted by deadline (most urgent first).
        
        Returns:
            Sorted list of valid packets
        """
        valid = self.get_valid_packets()
        return sorted(valid, key=lambda p: p.deadline)
    
    def get_sorted_by_value(self) -> List[Packet]:
        """
        Get packets sorted by value (highest first).
        
        Returns:
            Sorted list of valid packets
        """
        valid = self.get_valid_packets()
        return sorted(valid, key=lambda p: p.value, reverse=True)
    
    def is_empty(self) -> bool:
        """Check if queue has no valid packets."""
        return len(self.get_valid_packets()) == 0
    
    def size(self) -> int:
        """Get number of valid packets."""
        return len(self.get_valid_packets())
    
    def get_display_list(self, agent_id: str = "") -> List[str]:
        """
        Get formatted list for display.
        
        Args:
            agent_id: Agent identifier (A, B, etc.) for packet numbering
        
        Returns:
            List of formatted packet strings
        """
        valid = self.get_valid_packets()
        if not valid:
            return ["[Empty queue]"]
        
        display = []
        for i, packet in enumerate(valid):
            if agent_id:
                display.append(f"[{agent_id}-{i}] {packet}")
            else:
                display.append(f"[{i}] {packet}")
        return display
    
    def __repr__(self) -> str:
        """String representation of queue."""
        valid = self.get_valid_packets()
        if not valid:
            return "PacketQueue(empty)"
        return f"PacketQueue({len(valid)} packets: {valid})"


def generate_random_packet(turn: int = 0) -> Packet:
    """
    Generate a random packet according to game rules.
    
    Args:
        turn: Current turn number
        
    Returns:
        New packet with random value (1-10) and deadline (5-15)
    """
    value = random.randint(1, 10)
    deadline = random.randint(5, 15)
    return Packet(value=value, deadline=deadline, arrival_turn=turn)


# Test function
def test_packet_queue():
    """Test packet and queue functionality."""
    print("Testing Packet and Queue Mechanism")
    print("=" * 50)
    
    # Create test packets
    print("\n1. Creating test packets:")
    p1 = Packet(value=8, deadline=1, arrival_turn=1)
    p2 = Packet(value=5, deadline=3, arrival_turn=2)
    p3 = Packet(value=10, deadline=5, arrival_turn=3)
    print(f"  p1: {p1}")
    print(f"  p2: {p2}")
    print(f"  p3: {p3}")
    
    # Test priority calculation
    print("\n2. Priority scores:")
    print(f"  p1 priority: {p1.get_priority():.2f}")
    print(f"  p2 priority: {p2.get_priority():.2f}")
    print(f"  p3 priority: {p3.get_priority():.2f}")
    
    # Create queue and add packets
    print("\n3. Creating queue and adding packets:")
    queue = PacketQueue()
    queue.add_packet(p1)
    queue.add_packet(p2)
    queue.add_packet(p3)
    print(f"  Queue: {queue}")
    
    # Display queue
    print("\n4. Display format:")
    for line in queue.get_display_list("TEST"):
        print(f"  {line}")
    
    # Sort by different criteria
    print("\n5. Sorting:")
    print(f"  By priority: {queue.get_sorted_by_priority()}")
    print(f"  By deadline: {queue.get_sorted_by_deadline()}")
    print(f"  By value: {queue.get_sorted_by_value()}")
    
    # Update deadlines
    print("\n6. Updating deadlines (tick):")
    expired = queue.update_deadlines()
    print(f"  Expired packets: {expired}")
    print(f"  Queue after update: {queue}")
    
    # Display after update
    print("\n7. Display after deadline update:")
    for line in queue.get_display_list("TEST"):
        print(f"  {line}")
    
    # Generate random packet
    print("\n8. Generating random packet:")
    random_packet = generate_random_packet(turn=4)
    print(f"  Random packet: {random_packet}")
    queue.add_packet(random_packet)
    print(f"  Queue after adding: {queue}")
    
    print("\n✅ All tests completed successfully!")


if __name__ == "__main__":
    test_packet_queue()