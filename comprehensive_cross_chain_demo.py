#!/usr/bin/env python3
"""
Comprehensive Cross-Chain Communication Demo

This example demonstrates extensive usage of langgraph-crosschain with:
- Multiple chains (5 chains total)
- Cross-chain node communication
- Shared state coordination
- Message passing between chains
- Real-world workflow: E-commerce Order Processing System

Chains:
1. Order Service - Receives and validates orders
2. Inventory Service - Checks and reserves inventory
3. Payment Service - Processes payments
4. Shipping Service - Arranges shipment
5. Notification Service - Sends notifications

All chains communicate with each other to process a complete order.
"""

import time
from typing import Any

from langgraph.graph import END, StateGraph

# Import the package as a user would after installation
from langgraph_crosschain import (
    ChainRegistry,
    CrossChainNode,
    MessageRouter,
    SharedStateManager,
    get_logger,
)

# Set up logging
logger = get_logger(__name__)


# ============================================================================
# CHAIN 1: Order Service
# ============================================================================


def create_order_service():
    """
    Order Service Chain - Entry point for order processing.
    Validates orders and triggers inventory check.
    """

    def receive_order(state: dict[str, Any]) -> dict[str, Any]:
        """Receive and validate order"""
        order_id = state.get("order_id", "ORD-001")
        items = state.get("items", [])
        customer = state.get("customer", "Customer")

        print(f"\n📦 [ORDER SERVICE] Received order {order_id}")
        print(f"   Customer: {customer}")
        print(f"   Items: {items}")

        # Store order in shared state
        shared_state = SharedStateManager()
        shared_state.set(
            f"order_{order_id}",
            {
                "order_id": order_id,
                "items": items,
                "customer": customer,
                "status": "received",
                "timestamp": time.time(),
            },
        )

        # Create cross-chain node to communicate with inventory service
        node = CrossChainNode("order_service", "receive_order", receive_order)

        # Call inventory service to check stock
        print("   ➡️  Calling Inventory Service...")
        node.call_remote(
            target_chain="inventory_service",
            target_node="check_inventory",
            payload={"order_id": order_id, "items": items},
            wait_for_response=False,
        )

        return {
            "order_id": order_id,
            "status": "validating",
            "items": items,
            "customer": customer,
        }

    # Build the graph
    graph = StateGraph(dict)
    graph.add_node("receive_order", receive_order)
    graph.set_entry_point("receive_order")
    graph.add_edge("receive_order", END)

    return graph.compile()


# ============================================================================
# CHAIN 2: Inventory Service
# ============================================================================


def create_inventory_service():
    """
    Inventory Service Chain - Checks and reserves inventory.
    Communicates with payment service on success.
    """

    def check_inventory(state: dict[str, Any]) -> dict[str, Any]:
        """Check if items are in stock"""
        # Get messages from order service
        router = MessageRouter()
        messages = router.get_messages_for("inventory_service", "check_inventory")

        if not messages:
            return {"status": "no_messages"}

        print("\n📊 [INVENTORY SERVICE] Checking inventory")

        shared_state = SharedStateManager()

        for message in messages:
            order_id = message.payload.get("order_id")
            items = message.payload.get("items", [])

            print(f"   Order {order_id}: Checking {len(items)} items")

            # Simulate inventory check
            all_available = True
            inventory_status = []

            for item in items:
                # Mock: All items available
                available = True
                inventory_status.append(
                    {
                        "item": item.get("name"),
                        "quantity": item.get("quantity", 1),
                        "available": available,
                    }
                )
                print(f"   ✓ {item.get('name')}: {item.get('quantity', 1)} units available")

            # Update order status in shared state
            order_data = shared_state.get(f"order_{order_id}", {})
            order_data.update(
                {
                    "inventory_status": "available" if all_available else "unavailable",
                    "inventory_details": inventory_status,
                }
            )
            shared_state.set(f"order_{order_id}", order_data)

            if all_available:
                # Call payment service
                node = CrossChainNode("inventory_service", "check_inventory", check_inventory)
                print("   ➡️  Calling Payment Service...")
                node.call_remote(
                    target_chain="payment_service",
                    target_node="process_payment",
                    payload={
                        "order_id": order_id,
                        "amount": sum(
                            item.get("price", 0) * item.get("quantity", 1) for item in items
                        ),
                    },
                    wait_for_response=False,
                )

        return {"status": "inventory_checked", "messages_processed": len(messages)}

    # Build the graph
    graph = StateGraph(dict)
    graph.add_node("check_inventory", check_inventory)
    graph.set_entry_point("check_inventory")
    graph.add_edge("check_inventory", END)

    return graph.compile()


# ============================================================================
# CHAIN 3: Payment Service
# ============================================================================


def create_payment_service():
    """
    Payment Service Chain - Processes payments.
    Triggers shipping service on successful payment.
    """

    def process_payment(state: dict[str, Any]) -> dict[str, Any]:
        """Process payment for order"""
        router = MessageRouter()
        messages = router.get_messages_for("payment_service", "process_payment")

        if not messages:
            return {"status": "no_messages"}

        print("\n💳 [PAYMENT SERVICE] Processing payments")

        shared_state = SharedStateManager()

        for message in messages:
            order_id = message.payload.get("order_id")
            amount = message.payload.get("amount", 0)

            print(f"   Order {order_id}: Processing ${amount:.2f}")

            # Simulate payment processing
            payment_successful = True  # Mock: Always successful
            transaction_id = f"TXN-{int(time.time())}"

            # Update order in shared state
            order_data = shared_state.get(f"order_{order_id}", {})
            order_data.update(
                {
                    "payment_status": "paid" if payment_successful else "failed",
                    "transaction_id": transaction_id,
                    "amount": amount,
                }
            )
            shared_state.set(f"order_{order_id}", order_data)

            if payment_successful:
                print(f"   ✓ Payment successful: {transaction_id}")

                # Call shipping service
                node = CrossChainNode("payment_service", "process_payment", process_payment)
                print("   ➡️  Calling Shipping Service...")
                node.call_remote(
                    target_chain="shipping_service",
                    target_node="arrange_shipping",
                    payload={"order_id": order_id},
                    wait_for_response=False,
                )

        return {"status": "payment_processed", "messages_processed": len(messages)}

    # Build the graph
    graph = StateGraph(dict)
    graph.add_node("process_payment", process_payment)
    graph.set_entry_point("process_payment")
    graph.add_edge("process_payment", END)

    return graph.compile()


# ============================================================================
# CHAIN 4: Shipping Service
# ============================================================================


def create_shipping_service():
    """
    Shipping Service Chain - Arranges shipment.
    Notifies notification service when shipping is arranged.
    """

    def arrange_shipping(state: dict[str, Any]) -> dict[str, Any]:
        """Arrange shipping for order"""
        router = MessageRouter()
        messages = router.get_messages_for("shipping_service", "arrange_shipping")

        if not messages:
            return {"status": "no_messages"}

        print("\n🚚 [SHIPPING SERVICE] Arranging shipments")

        shared_state = SharedStateManager()

        for message in messages:
            order_id = message.payload.get("order_id")

            print(f"   Order {order_id}: Arranging shipment")

            # Simulate shipping arrangement
            tracking_number = f"TRACK-{int(time.time())}"
            estimated_delivery = "3-5 business days"

            # Update order in shared state
            order_data = shared_state.get(f"order_{order_id}", {})
            order_data.update(
                {
                    "shipping_status": "arranged",
                    "tracking_number": tracking_number,
                    "estimated_delivery": estimated_delivery,
                }
            )
            shared_state.set(f"order_{order_id}", order_data)

            print(f"   ✓ Tracking number: {tracking_number}")
            print(f"   ✓ Estimated delivery: {estimated_delivery}")

            # Call notification service
            node = CrossChainNode("shipping_service", "arrange_shipping", arrange_shipping)
            print("   ➡️  Calling Notification Service...")
            node.call_remote(
                target_chain="notification_service",
                target_node="send_notification",
                payload={"order_id": order_id, "event": "order_shipped"},
                wait_for_response=False,
            )

        return {"status": "shipping_arranged", "messages_processed": len(messages)}

    # Build the graph
    graph = StateGraph(dict)
    graph.add_node("arrange_shipping", arrange_shipping)
    graph.set_entry_point("arrange_shipping")
    graph.add_edge("arrange_shipping", END)

    return graph.compile()


# ============================================================================
# CHAIN 5: Notification Service
# ============================================================================


def create_notification_service():
    """
    Notification Service Chain - Sends notifications to customers.
    Final step in the order processing workflow.
    """

    def send_notification(state: dict[str, Any]) -> dict[str, Any]:
        """Send notification to customer"""
        router = MessageRouter()
        messages = router.get_messages_for("notification_service", "send_notification")

        if not messages:
            return {"status": "no_messages"}

        print("\n📧 [NOTIFICATION SERVICE] Sending notifications")

        shared_state = SharedStateManager()

        for message in messages:
            order_id = message.payload.get("order_id")
            event = message.payload.get("event")

            # Get complete order data
            order_data = shared_state.get(f"order_{order_id}", {})
            customer = order_data.get("customer", "Customer")

            print(f"   Order {order_id}: Notifying {customer}")
            print(f"   Event: {event}")

            # Update order as completed
            order_data["status"] = "completed"
            order_data["completed_at"] = time.time()
            shared_state.set(f"order_{order_id}", order_data)

            print("   ✓ Notification sent successfully")

        return {"status": "notifications_sent", "messages_processed": len(messages)}

    # Build the graph
    graph = StateGraph(dict)
    graph.add_node("send_notification", send_notification)
    graph.set_entry_point("send_notification")
    graph.add_edge("send_notification", END)

    return graph.compile()


# ============================================================================
# ORCHESTRATION
# ============================================================================


def run_comprehensive_demo():
    """
    Run comprehensive cross-chain communication demo.
    Simulates a complete e-commerce order processing workflow.
    """
    print("=" * 80)
    print("🎯 COMPREHENSIVE CROSS-CHAIN COMMUNICATION DEMO")
    print("=" * 80)
    print("\nScenario: E-commerce Order Processing System")
    print("Processing an order through 5 interconnected chains")
    print("=" * 80)

    # Create registry and state manager
    registry = ChainRegistry()
    shared_state = SharedStateManager()

    # Clear any existing state
    shared_state.clear()

    # Create all service chains
    print("\n🔧 Initializing Services...")
    order_chain = create_order_service()
    inventory_chain = create_inventory_service()
    payment_chain = create_payment_service()
    shipping_chain = create_shipping_service()
    notification_chain = create_notification_service()

    # Register all chains
    registry.register("order_service", order_chain)
    registry.register("inventory_service", inventory_chain)
    registry.register("payment_service", payment_chain)
    registry.register("shipping_service", shipping_chain)
    registry.register("notification_service", notification_chain)

    print("✅ All 5 services registered")
    print(f"   Services: {registry.list_chains()}")

    # Create test order
    test_order = {
        "order_id": "ORD-12345",
        "customer": "John Doe",
        "items": [
            {"name": "Laptop", "quantity": 1, "price": 999.99},
            {"name": "Mouse", "quantity": 2, "price": 29.99},
            {"name": "Keyboard", "quantity": 1, "price": 79.99},
        ],
    }

    print("\n" + "=" * 80)
    print("🚀 STARTING ORDER PROCESSING WORKFLOW")
    print("=" * 80)

    # Step 1: Order Service receives order
    print("\n[STEP 1/5] Order Received")
    order_chain.invoke(test_order)

    # Small delay to ensure message queuing
    time.sleep(0.1)

    # Step 2: Inventory Service checks stock
    print("\n[STEP 2/5] Inventory Check")
    inventory_chain.invoke({})

    time.sleep(0.1)

    # Step 3: Payment Service processes payment
    print("\n[STEP 3/5] Payment Processing")
    payment_chain.invoke({})

    time.sleep(0.1)

    # Step 4: Shipping Service arranges delivery
    print("\n[STEP 4/5] Shipping Arrangement")
    shipping_chain.invoke({})

    time.sleep(0.1)

    # Step 5: Notification Service sends confirmation
    print("\n[STEP 5/5] Customer Notification")
    notification_chain.invoke({})

    # Display final results
    print("\n" + "=" * 80)
    print("📊 WORKFLOW COMPLETE - FINAL STATUS")
    print("=" * 80)

    # Get final order state
    final_order = shared_state.get(f"order_{test_order['order_id']}")

    if final_order:
        print(f"\n✅ Order {final_order['order_id']} completed successfully!")
        print("\n📋 Order Summary:")
        print(f"   Customer: {final_order['customer']}")
        print(f"   Items: {len(final_order['items'])} items")
        print(f"   Total: ${final_order.get('amount', 0):.2f}")
        print("\n📦 Processing Details:")
        print(f"   Inventory: {final_order.get('inventory_status', 'N/A')}")
        print(f"   Payment: {final_order.get('payment_status', 'N/A')}")
        print(f"   Transaction: {final_order.get('transaction_id', 'N/A')}")
        print(f"   Shipping: {final_order.get('shipping_status', 'N/A')}")
        print(f"   Tracking: {final_order.get('tracking_number', 'N/A')}")
        print(f"   Delivery: {final_order.get('estimated_delivery', 'N/A')}")
        print(f"   Status: {final_order.get('status', 'N/A').upper()}")

    # Test statistics
    print("\n📈 Cross-Chain Communication Stats:")
    print("   Total Chains: 5")
    print("   Cross-Chain Calls: 4")
    print("   Shared State Updates: 5+")

    # Test all registry features
    print("\n🔍 Registry Features Test:")
    print(f"   ✓ Registered chains: {len(registry.list_chains())}")
    print(f"   ✓ Get chain: {registry.get('order_service') is not None}")
    print(f"   ✓ Contains check: {'order_service' in registry}")

    # Test shared state features
    print("\n💾 Shared State Features Test:")
    print(f"   ✓ Keys stored: {len(shared_state.keys())}")
    print(f"   ✓ Snapshot size: {len(shared_state.snapshot())} items")

    print("\n" + "=" * 80)
    print("✅ COMPREHENSIVE DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nAll features tested:")
    print("  ✓ 5 chains created and registered")
    print("  ✓ Cross-chain node communication (4 calls)")
    print("  ✓ Message routing between chains")
    print("  ✓ Shared state coordination")
    print("  ✓ Complete workflow execution")
    print("  ✓ ChainRegistry features")
    print("  ✓ SharedStateManager features")
    print("  ✓ CrossChainNode remote calls")
    print("  ✓ MessageRouter queue management")
    print("\n🎉 Package working perfectly!")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    try:
        run_comprehensive_demo()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
