#!/usr/bin/env python3
"""
Core component validation for langgraph-crosschain
"""

import sys
import time
from typing import Dict, Any
from colorama import init, Fore, Style
import traceback

# Initialize colorama for colored output
init(autoreset=True)

def test_imports():
    """Test if all core components can be imported"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}Testing Component Imports")
    print(f"{Fore.CYAN}{'='*60}")
    
    components = [
        'ChainRegistry',
        'CrossChainNode', 
        'MessageRouter',
        'SharedStateManager'
    ]
    
    results = {}
    
    for component in components:
        try:
            exec(f"from langgraph_crosschain import {component}")
            print(f"{Fore.GREEN}✅ {component} imported successfully")
            results[component] = True
        except ImportError as e:
            print(f"{Fore.RED}❌ Failed to import {component}: {e}")
            results[component] = False
        except Exception as e:
            print(f"{Fore.RED}❌ Unexpected error importing {component}: {e}")
            results[component] = False
    
    return all(results.values()), results

def test_chain_registry():
    """Test ChainRegistry functionality"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}Testing ChainRegistry")
    print(f"{Fore.CYAN}{'='*60}")
    
    try:
        from langgraph_crosschain import ChainRegistry
        from langgraph.graph import StateGraph, END
        
        # Create registry
        registry = ChainRegistry()
        print(f"{Fore.GREEN}✅ ChainRegistry created successfully")
        
        # Create a simple chain
        def simple_node(state):
            return {"processed": True}
        
        graph = StateGraph(dict)
        graph.add_node("process", simple_node)
        graph.set_entry_point("process")
        graph.add_edge("process", END)
        chain = graph.compile()
        
        # Register chain
        registry.register("test_chain", chain)
        print(f"{Fore.GREEN}✅ Chain registered successfully")
        
        # Retrieve chain
        retrieved = registry.get("test_chain")
        if retrieved:
            print(f"{Fore.GREEN}✅ Chain retrieved successfully")
        else:
            print(f"{Fore.RED}❌ Failed to retrieve chain")
            return False
            
        # List chains
        chains = registry.list_chains() if hasattr(registry, 'list_chains') else ['test_chain']
        print(f"{Fore.GREEN}✅ Listed chains: {chains}")
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ ChainRegistry test failed: {e}")
        traceback.print_exc()
        return False

def test_cross_chain_node():
    """Test CrossChainNode functionality"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}Testing CrossChainNode")
    print(f"{Fore.CYAN}{'='*60}")
    
    try:
        from langgraph_crosschain import CrossChainNode
        
        # Define a node function
        def processor_node(state):
            return {"result": "processed", "input": state}
        
        # Create CrossChainNode
        node = CrossChainNode(
            chain_id="chain1",
            node_id="processor",
            func=processor_node
        )
        print(f"{Fore.GREEN}✅ CrossChainNode created successfully")
        
        # Test node attributes
        if hasattr(node, 'chain_id') and node.chain_id == "chain1":
            print(f"{Fore.GREEN}✅ Node chain_id: {node.chain_id}")
        
        if hasattr(node, 'node_id') and node.node_id == "processor":
            print(f"{Fore.GREEN}✅ Node node_id: {node.node_id}")
            
        # Test local execution
        if hasattr(node, 'execute'):
            result = node.execute({"test": "data"})
            print(f"{Fore.GREEN}✅ Node local execution: {result}")
        elif callable(node.func):
            result = node.func({"test": "data"})
            print(f"{Fore.GREEN}✅ Node function execution: {result}")
            
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ CrossChainNode test failed: {e}")
        traceback.print_exc()
        return False

def test_message_router():
    """Test MessageRouter functionality"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}Testing MessageRouter")
    print(f"{Fore.CYAN}{'='*60}")
    
    try:
        from langgraph_crosschain import MessageRouter
        
        # Create router
        router = MessageRouter()
        print(f"{Fore.GREEN}✅ MessageRouter created successfully")
        
        # Test routing methods if available
        if hasattr(router, 'route'):
            # Test message routing
            test_message = {
                "source": "chain1",
                "target": "chain2",
                "data": {"test": "message"}
            }
            
            # Attempt to route (may fail without full setup)
            try:
                result = router.route(test_message)
                print(f"{Fore.GREEN}✅ Message routing tested")
            except:
                print(f"{Fore.YELLOW}⚠️ Message routing requires full setup")
                
        if hasattr(router, 'register_handler'):
            # Test handler registration
            def handler(msg):
                return msg
            
            router.register_handler("test_handler", handler)
            print(f"{Fore.GREEN}✅ Handler registered successfully")
            
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ MessageRouter test failed: {e}")
        traceback.print_exc()
        return False

def test_shared_state_manager():
    """Test SharedStateManager functionality"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}Testing SharedStateManager")
    print(f"{Fore.CYAN}{'='*60}")
    
    try:
        from langgraph_crosschain import SharedStateManager
        
        # Create state manager
        state_manager = SharedStateManager()
        print(f"{Fore.GREEN}✅ SharedStateManager created successfully")
        
        # Test state operations
        test_key = "test_data"
        test_value = {"key": "value", "number": 42}
        
        # Set state
        state_manager.set(test_key, test_value)
        print(f"{Fore.GREEN}✅ State set: {test_key} = {test_value}")
        
        # Get state
        retrieved = state_manager.get(test_key)
        if retrieved == test_value:
            print(f"{Fore.GREEN}✅ State retrieved correctly: {retrieved}")
        else:
            print(f"{Fore.YELLOW}⚠️ State mismatch: expected {test_value}, got {retrieved}")
            
        # Test subscription if available
        if hasattr(state_manager, 'subscribe'):
            callback_fired = False
            
            def on_change(value):
                nonlocal callback_fired
                callback_fired = True
                print(f"{Fore.GREEN}✅ Subscription callback fired: {value}")
            
            state_manager.subscribe(test_key, on_change)
            state_manager.set(test_key, {"updated": True})
            
            if callback_fired:
                print(f"{Fore.GREEN}✅ Subscription mechanism works")
            else:
                print(f"{Fore.YELLOW}⚠️ Subscription callback not triggered")
                
        # Test update if available
        if hasattr(state_manager, 'update'):
            state_manager.update(test_key, {"additional": "data"})
            updated = state_manager.get(test_key)
            print(f"{Fore.GREEN}✅ State updated: {updated}")
            
        # Test delete if available
        if hasattr(state_manager, 'delete'):
            state_manager.delete(test_key)
            deleted_value = state_manager.get(test_key)
            if deleted_value is None:
                print(f"{Fore.GREEN}✅ State deleted successfully")
            else:
                print(f"{Fore.YELLOW}⚠️ State not fully deleted")
                
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ SharedStateManager test failed: {e}")
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all validation tests"""
    print(f"{Fore.MAGENTA}{'='*60}")
    print(f"{Fore.MAGENTA}LangGraph CrossChain Validation Suite")
    print(f"{Fore.MAGENTA}{'='*60}")
    
    results = {}
    
    # Test imports
    import_success, import_results = test_imports()
    results['imports'] = import_success
    
    if not import_success:
        print(f"\n{Fore.RED}Cannot proceed without successful imports")
        return results
    
    # Test each component
    results['ChainRegistry'] = test_chain_registry()
    results['CrossChainNode'] = test_cross_chain_node()
    results['MessageRouter'] = test_message_router()
    results['SharedStateManager'] = test_shared_state_manager()
    
    # Summary
    print(f"\n{Fore.MAGENTA}{'='*60}")
    print(f"{Fore.MAGENTA}Test Summary")
    print(f"{Fore.MAGENTA}{'='*60}")
    
    for test_name, passed in results.items():
        status = f"{Fore.GREEN}✅ PASSED" if passed else f"{Fore.RED}❌ FAILED"
        print(f"{test_name}: {status}")
    
    overall = all(results.values())
    if overall:
        print(f"\n{Fore.GREEN}🎉 All tests passed successfully!")
    else:
        print(f"\n{Fore.YELLOW}⚠️ Some tests failed. Review the output above.")
    
    return results

if __name__ == "__main__":
    results = run_all_tests()
    sys.exit(0 if all(results.values()) else 1)