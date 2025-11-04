#!/usr/bin/env python3
"""
Example usage of langgraph-crosschain package
Demonstrates practical implementation patterns
"""

from typing import Dict, Any, List
import json
import time
from colorama import init, Fore

# Initialize colorama
init(autoreset=True)

def example_multi_agent_system():
    """
    Example: Multi-Agent System with specialized chains
    Use case: AI agents that collaborate on complex tasks
    """
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}Example: Multi-Agent System")
    print(f"{Fore.CYAN}{'='*60}")
    
    try:
        from langgraph_crosschain import ChainRegistry, CrossChainNode, SharedStateManager
        from langgraph.graph import StateGraph, END
        
        # Create shared components
        registry = ChainRegistry()
        shared_state = SharedStateManager()
        
        # === Research Agent Chain ===
        def research_node(state):
            """Research agent that gathers information"""
            query = state.get('query', '')
            
            # Simulate research
            research_results = {
                'sources': ['source1.pdf', 'source2.html', 'source3.json'],
                'key_findings': [
                    'Finding 1: Data shows positive trend',
                    'Finding 2: Market analysis confirms hypothesis',
                    'Finding 3: User feedback is favorable'
                ],
                'confidence': 0.85
            }
            
            # Store in shared state for other agents
            shared_state.set('research_results', research_results)
            
            return {'research': research_results, 'status': 'completed'}
        
        # Build research chain
        research_graph = StateGraph(dict)
        research_graph.add_node("research", research_node)
        research_graph.set_entry_point("research")
        research_graph.add_edge("research", END)
        research_chain = research_graph.compile()
        
        # === Analysis Agent Chain ===
        def analysis_node(state):
            """Analysis agent that processes research results"""
            # Get research results from shared state
            research_results = shared_state.get('research_results')
            
            if not research_results:
                return {'error': 'No research results found'}
            
            # Perform analysis
            analysis = {
                'summary': 'Positive indicators across all metrics',
                'recommendations': [
                    'Proceed with implementation',
                    'Monitor key metrics',
                    'Prepare scaling strategy'
                ],
                'risk_assessment': 'Low to Medium',
                'confidence_score': research_results.get('confidence', 0) * 0.9
            }
            
            # Store analysis results
            shared_state.set('analysis_results', analysis)
            
            return {'analysis': analysis, 'status': 'completed'}
        
        # Build analysis chain
        analysis_graph = StateGraph(dict)
        analysis_graph.add_node("analyze", analysis_node)
        analysis_graph.set_entry_point("analyze")
        analysis_graph.add_edge("analyze", END)
        analysis_chain = analysis_graph.compile()
        
        # === Decision Agent Chain ===
        def decision_node(state):
            """Decision agent that makes final recommendations"""
            # Get both research and analysis from shared state
            research = shared_state.get('research_results')
            analysis = shared_state.get('analysis_results')
            
            if not research or not analysis:
                return {'error': 'Missing required data'}
            
            # Make decision
            confidence = analysis.get('confidence_score', 0)
            decision = {
                'action': 'APPROVE' if confidence > 0.7 else 'REVIEW',
                'confidence': confidence,
                'reasoning': analysis.get('summary', ''),
                'next_steps': analysis.get('recommendations', []),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return {'decision': decision, 'status': 'completed'}
        
        # Build decision chain  
        decision_graph = StateGraph(dict)
        decision_graph.add_node("decide", decision_node)
        decision_graph.set_entry_point("decide")
        decision_graph.add_edge("decide", END)
        decision_chain = decision_graph.compile()
        
        # Register all chains
        registry.register("research_agent", research_chain)
        registry.register("analysis_agent", analysis_chain)
        registry.register("decision_agent", decision_chain)
        
        print(f"{Fore.GREEN}✅ Multi-agent system initialized")
        
        # Execute the multi-agent workflow
        print(f"\n{Fore.YELLOW}Executing multi-agent workflow...")
        
        # Step 1: Research
        research_result = research_chain.invoke({'query': 'Market analysis for Q4'})
        print(f"{Fore.GREEN}✅ Research completed: {research_result['status']}")
        
        # Step 2: Analysis
        analysis_result = analysis_chain.invoke({})
        print(f"{Fore.GREEN}✅ Analysis completed: {analysis_result['status']}")
        
        # Step 3: Decision
        decision_result = decision_chain.invoke({})
        print(f"{Fore.GREEN}✅ Decision made: {decision_result['decision']['action']}")
        
        # Display final decision
        print(f"\n{Fore.CYAN}Final Decision:")
        print(json.dumps(decision_result['decision'], indent=2))
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Multi-agent example failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def example_workflow_orchestration():
    """
    Example: Complex workflow orchestration with cross-chain calls
    Use case: Data pipeline with multiple processing stages
    """
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}Example: Workflow Orchestration")
    print(f"{Fore.CYAN}{'='*60}")
    
    try:
        from langgraph_crosschain import ChainRegistry, CrossChainNode
        from langgraph.graph import StateGraph, END
        
        registry = ChainRegistry()
        
        # === Data Ingestion Chain ===
        def ingest_data(state):
            """Ingest raw data from sources"""
            sources = state.get('sources', [])
            
            data = []
            for source in sources:
                # Simulate data ingestion
                data.append({
                    'source': source,
                    'records': 1000,
                    'timestamp': time.time()
                })
            
            return {'raw_data': data, 'ingestion_status': 'completed'}
        
        ingestion_graph = StateGraph(dict)
        ingestion_graph.add_node("ingest", ingest_data)
        ingestion_graph.set_entry_point("ingest")
        ingestion_graph.add_edge("ingest", END)
        
        # === Data Validation Chain ===
        def validate_data(state):
            """Validate ingested data"""
            raw_data = state.get('raw_data', [])
            
            validation_results = []
            for item in raw_data:
                validation_results.append({
                    'source': item['source'],
                    'valid': item['records'] > 0,
                    'issues': [] if item['records'] > 0 else ['No records found']
                })
            
            return {
                'validation_results': validation_results,
                'all_valid': all(v['valid'] for v in validation_results)
            }
        
        validation_graph = StateGraph(dict)
        validation_graph.add_node("validate", validate_data)
        validation_graph.set_entry_point("validate")
        validation_graph.add_edge("validate", END)
        
        # === Data Transformation Chain ===
        def transform_data(state):
            """Transform validated data"""
            raw_data = state.get('raw_data', [])
            validation = state.get('validation_results', [])
            
            transformed = []
            for data, val in zip(raw_data, validation):
                if val['valid']:
                    transformed.append({
                        'source': data['source'],
                        'processed_records': data['records'],
                        'transformations': ['normalized', 'enriched', 'indexed']
                    })
            
            return {'transformed_data': transformed, 'transformation_status': 'completed'}
        
        transform_graph = StateGraph(dict)
        transform_graph.add_node("transform", transform_data)
        transform_graph.set_entry_point("transform")
        transform_graph.add_edge("transform", END)
        
        # Register chains
        registry.register("ingestion", ingestion_graph.compile())
        registry.register("validation", validation_graph.compile())
        registry.register("transformation", transform_graph.compile())
        
        print(f"{Fore.GREEN}✅ Workflow chains registered")
        
        # Execute orchestrated workflow
        print(f"\n{Fore.YELLOW}Executing orchestrated workflow...")
        
        # Initial state
        workflow_state = {
            'sources': ['database_1', 'api_endpoint', 'file_system']
        }
        
        # Step 1: Ingestion
        ingestion_result = registry.get("ingestion").invoke(workflow_state)
        workflow_state.update(ingestion_result)
        print(f"{Fore.GREEN}✅ Data ingested from {len(workflow_state['raw_data'])} sources")
        
        # Step 2: Validation
        validation_result = registry.get("validation").invoke(workflow_state)
        workflow_state.update(validation_result)
        print(f"{Fore.GREEN}✅ Validation completed - All valid: {workflow_state['all_valid']}")
        
        # Step 3: Transformation
        if workflow_state['all_valid']:
            transform_result = registry.get("transformation").invoke(workflow_state)
            workflow_state.update(transform_result)
            print(f"{Fore.GREEN}✅ Data transformation completed")
        else:
            print(f"{Fore.YELLOW}⚠️ Skipping transformation due to validation failures")
        
        # Display results
        print(f"\n{Fore.CYAN}Workflow Results:")
        for key in ['ingestion_status', 'all_valid', 'transformation_status']:
            if key in workflow_state:
                print(f"  {key}: {workflow_state[key]}")
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Workflow orchestration example failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def example_distributed_processing():
    """
    Example: Distributed processing with worker chains
    Use case: Parallel processing of large datasets
    """
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}Example: Distributed Processing")
    print(f"{Fore.CYAN}{'='*60}")
    
    try:
        from langgraph_crosschain import ChainRegistry, CrossChainNode, SharedStateManager
        from langgraph.graph import StateGraph, END
        
        registry = ChainRegistry()
        shared_state = SharedStateManager()
        
        # === Master Coordinator Chain ===
        def coordinator_node(state):
            """Coordinator that distributes work"""
            dataset = state.get('dataset', [])
            num_workers = state.get('num_workers', 3)
            
            # Split dataset into chunks
            chunk_size = len(dataset) // num_workers
            work_packages = []
            
            for i in range(num_workers):
                start_idx = i * chunk_size
                end_idx = start_idx + chunk_size if i < num_workers - 1 else len(dataset)
                
                work_package = {
                    'worker_id': f'worker_{i+1}',
                    'data_chunk': dataset[start_idx:end_idx],
                    'task': 'process'
                }
                work_packages.append(work_package)
                
                # Store work package in shared state
                shared_state.set(f'work_package_{i+1}', work_package)
            
            return {
                'work_packages': work_packages,
                'distribution_status': 'completed',
                'total_items': len(dataset)
            }
        
        coordinator_graph = StateGraph(dict)
        coordinator_graph.add_node("coordinate", coordinator_node)
        coordinator_graph.set_entry_point("coordinate")
        coordinator_graph.add_edge("coordinate", END)
        
        # === Worker Chain Template ===
        def create_worker_chain(worker_id: int):
            def worker_node(state):
                """Worker that processes assigned data chunk"""
                # Get work package from shared state
                work_package = shared_state.get(f'work_package_{worker_id}')
                
                if not work_package:
                    return {'error': f'No work package for worker_{worker_id}'}
                
                # Process data chunk
                data_chunk = work_package['data_chunk']
                processed = []
                
                for item in data_chunk:
                    # Simulate processing
                    processed.append({
                        'original': item,
                        'processed': item * 2,  # Simple transformation
                        'worker': f'worker_{worker_id}'
                    })
                
                # Store results in shared state
                shared_state.set(f'worker_{worker_id}_results', processed)
                
                return {
                    'worker_id': f'worker_{worker_id}',
                    'items_processed': len(processed),
                    'status': 'completed'
                }
            
            graph = StateGraph(dict)
            graph.add_node("process", worker_node)
            graph.set_entry_point("process")
            graph.add_edge("process", END)
            
            return graph.compile()
        
        # === Aggregator Chain ===
        def aggregator_node(state):
            """Aggregator that combines worker results"""
            num_workers = state.get('num_workers', 3)
            
            all_results = []
            for i in range(1, num_workers + 1):
                worker_results = shared_state.get(f'worker_{i}_results')
                if worker_results:
                    all_results.extend(worker_results)
            
            # Aggregate statistics
            aggregation = {
                'total_processed': len(all_results),
                'workers_completed': num_workers,
                'average_per_worker': len(all_results) // num_workers if num_workers > 0 else 0,
                'final_results': all_results
            }
            
            return {'aggregation': aggregation, 'status': 'completed'}
        
        aggregator_graph = StateGraph(dict)
        aggregator_graph.add_node("aggregate", aggregator_node)
        aggregator_graph.set_entry_point("aggregate")
        aggregator_graph.add_edge("aggregate", END)
        
        # Register chains
        registry.register("coordinator", coordinator_graph.compile())
        
        # Create and register worker chains
        num_workers = 3
        for i in range(1, num_workers + 1):
            registry.register(f"worker_{i}", create_worker_chain(i))
        
        registry.register("aggregator", aggregator_graph.compile())
        
        print(f"{Fore.GREEN}✅ Distributed system initialized with {num_workers} workers")
        
        # Execute distributed processing
        print(f"\n{Fore.YELLOW}Executing distributed processing...")
        
        # Sample dataset
        dataset = list(range(1, 31))  # Process numbers 1-30
        
        # Step 1: Distribute work
        distribution_result = registry.get("coordinator").invoke({
            'dataset': dataset,
            'num_workers': num_workers
        })
        print(f"{Fore.GREEN}✅ Work distributed: {distribution_result['total_items']} items to {num_workers} workers")
        
        # Step 2: Process in parallel (simulated)
        worker_results = []
        for i in range(1, num_workers + 1):
            worker_result = registry.get(f"worker_{i}").invoke({})
            worker_results.append(worker_result)
            print(f"{Fore.GREEN}✅ Worker {i} completed: {worker_result['items_processed']} items")
        
        # Step 3: Aggregate results
        aggregation_result = registry.get("aggregator").invoke({
            'num_workers': num_workers
        })
        
        final_stats = aggregation_result['aggregation']
        print(f"\n{Fore.CYAN}Processing Complete:")
        print(f"  Total items processed: {final_stats['total_processed']}")
        print(f"  Workers used: {final_stats['workers_completed']}")
        print(f"  Average per worker: {final_stats['average_per_worker']}")
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Distributed processing example failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all examples"""
    print(f"{Fore.MAGENTA}{'='*60}")
    print(f"{Fore.MAGENTA}LangGraph CrossChain - Example Usage")
    print(f"{Fore.MAGENTA}{'='*60}")
    
    examples = [
        ("Multi-Agent System", example_multi_agent_system),
        ("Workflow Orchestration", example_workflow_orchestration),
        ("Distributed Processing", example_distributed_processing)
    ]
    
    results = {}
    
    for name, example_func in examples:
        print(f"\n{Fore.YELLOW}Running: {name}")
        success = example_func()
        results[name] = success
    
    # Summary
    print(f"\n{Fore.MAGENTA}{'='*60}")
    print(f"{Fore.MAGENTA}Example Summary")
    print(f"{Fore.MAGENTA}{'='*60}")
    
    for name, success in results.items():
        status = f"{Fore.GREEN}✅ SUCCESS" if success else f"{Fore.RED}❌ FAILED"
        print(f"{name}: {status}")
    
    if all(results.values()):
        print(f"\n{Fore.GREEN}All examples completed successfully!")
    else:
        print(f"\n{Fore.YELLOW}Some examples failed. Check implementation.")

if __name__ == "__main__":
    main()