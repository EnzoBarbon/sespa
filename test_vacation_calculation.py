import datetime
import json

def calculate_non_overlapping_vacation_days(data):
    """
    Calculate vacation days that don't overlap with contract periods.
    Returns both the total days and the specific non-overlapping periods.
    """
    vacations = [item for item in data if item["isVacaciones"]]
    contracts = [item for item in data if not item["isVacaciones"]]
    
    total_non_overlapping_days = 0
    non_overlapping_periods = []
    
    for vacation in vacations:
        if not vacation["fechaAlta"] or not vacation["fechaBaja"]:
            continue
            
        try:
            vac_start = datetime.datetime.strptime(vacation["fechaAlta"], "%d/%m/%Y")
            vac_end = datetime.datetime.strptime(vacation["fechaBaja"], "%d/%m/%Y")
        except ValueError:
            continue
            
        # Find overlapping contracts
        overlapping_periods = []
        
        for contract in contracts:
            if not contract["fechaAlta"]:
                continue
                
            try:
                contract_start = datetime.datetime.strptime(contract["fechaAlta"], "%d/%m/%Y")
                # If contract has no end date, assume it's still active (use today)
                if contract["fechaBaja"]:
                    contract_end = datetime.datetime.strptime(contract["fechaBaja"], "%d/%m/%Y")
                else:
                    contract_end = datetime.datetime.now()
                    
                # Check if vacation overlaps with contract
                if vac_start <= contract_end and vac_end >= contract_start:
                    # Calculate overlapping period
                    overlap_start = max(vac_start, contract_start)
                    overlap_end = min(vac_end, contract_end)
                    overlapping_periods.append((overlap_start, overlap_end))
                    
            except ValueError:
                continue
        
        # Calculate non-overlapping periods for this vacation
        if not overlapping_periods:
            # No overlap, count all vacation days
            vacation_days = (vac_end - vac_start).days + 1
            total_non_overlapping_days += vacation_days
            non_overlapping_periods.append({
                "start": vac_start.strftime("%d/%m/%Y"),
                "end": vac_end.strftime("%d/%m/%Y"),
                "days": vacation_days
            })
        else:
            # Merge overlapping periods and calculate non-overlapping segments
            overlapping_periods.sort()
            merged_overlaps = []
            
            for overlap in overlapping_periods:
                if not merged_overlaps or merged_overlaps[-1][1] < overlap[0]:
                    merged_overlaps.append(overlap)
                else:
                    merged_overlaps[-1] = (merged_overlaps[-1][0], max(merged_overlaps[-1][1], overlap[1]))
            
            # Find non-overlapping segments within this vacation
            current_pos = vac_start
            
            for overlap_start, overlap_end in merged_overlaps:
                # Add period before this overlap (if any)
                if current_pos < overlap_start:
                    segment_end = overlap_start - datetime.timedelta(days=1)
                    segment_days = (segment_end - current_pos).days + 1
                    if segment_days > 0:
                        total_non_overlapping_days += segment_days
                        non_overlapping_periods.append({
                            "start": current_pos.strftime("%d/%m/%Y"),
                            "end": segment_end.strftime("%d/%m/%Y"),
                            "days": segment_days
                        })
                
                # Move current position past this overlap
                current_pos = overlap_end + datetime.timedelta(days=1)
            
            # Add remaining period after all overlaps (if any)
            if current_pos <= vac_end:
                segment_days = (vac_end - current_pos).days + 1
                if segment_days > 0:
                    total_non_overlapping_days += segment_days
                    non_overlapping_periods.append({
                        "start": current_pos.strftime("%d/%m/%Y"),
                        "end": vac_end.strftime("%d/%m/%Y"),
                        "days": segment_days
                    })
    
    return total_non_overlapping_days, non_overlapping_periods

def run_test_case(name, data, expected_result, expected_periods=None):
    """Run a single test case and return the result."""
    print(f"\n--- Test Case: {name} ---")
    total_days, periods = calculate_non_overlapping_vacation_days(data)
    print(f"Expected days: {expected_result}, Got: {total_days}")
    
    if expected_periods is not None:
        print(f"Expected periods: {len(expected_periods)}, Got: {len(periods)}")
        print("Periods found:")
        for period in periods:
            print(f"  {period['start']} to {period['end']} ({period['days']} days)")
    
    if total_days == expected_result:
        if expected_periods is None or len(periods) == len(expected_periods):
            print("✅ PASS")
            return True
        else:
            print("❌ FAIL - Period count mismatch")
            return False
    else:
        print("❌ FAIL - Day count mismatch")
        print("Data:")
        for item in data:
            print(f"  {item}")
        return False

def run_all_tests():
    """Run all test cases."""
    total_tests = 0
    passed_tests = 0
    
    # Test Case 1: No overlaps - all vacation days should be counted
    test1_data = [
        {"isVacaciones": True, "fechaAlta": "01/01/2020", "fechaBaja": "05/01/2020"},  # 5 days
        {"isVacaciones": True, "fechaAlta": "10/01/2020", "fechaBaja": "12/01/2020"},  # 3 days
        {"isVacaciones": False, "fechaAlta": "20/01/2020", "fechaBaja": "25/01/2020"}  # contract after vacations
    ]
    total_tests += 1
    if run_test_case("No overlaps", test1_data, 8):
        passed_tests += 1
    
    # Test Case 2: Complete overlap - no vacation days should be counted
    test2_data = [
        {"isVacaciones": True, "fechaAlta": "05/01/2020", "fechaBaja": "10/01/2020"},  # 6 days vacation
        {"isVacaciones": False, "fechaAlta": "01/01/2020", "fechaBaja": "15/01/2020"}  # contract covers vacation
    ]
    total_tests += 1
    if run_test_case("Complete overlap", test2_data, 0):
        passed_tests += 1
    
    # Test Case 3: Partial overlap - your example case
    test3_data = [
        {"isVacaciones": True, "fechaAlta": "01/01/2020", "fechaBaja": "10/01/2020"},  # 10 days vacation
        {"isVacaciones": False, "fechaAlta": "06/01/2020", "fechaBaja": "20/01/2020"}  # contract starts on 6th
    ]
    expected_periods_3 = [{"start": "01/01/2020", "end": "05/01/2020", "days": 5}]
    total_tests += 1
    if run_test_case("Partial overlap (your example)", test3_data, 5, expected_periods_3):
        passed_tests += 1
    
    # Test Case 4: Multiple contracts with gaps
    test4_data = [
        {"isVacaciones": True, "fechaAlta": "01/01/2020", "fechaBaja": "20/01/2020"},  # 20 days vacation
        {"isVacaciones": False, "fechaAlta": "05/01/2020", "fechaBaja": "08/01/2020"},  # contract 1: 4 days
        {"isVacaciones": False, "fechaAlta": "15/01/2020", "fechaBaja": "18/01/2020"}   # contract 2: 4 days
    ]
    # Total vacation: 20 days, overlaps: 4 + 4 = 8 days, non-overlapping: 12 days
    total_tests += 1
    if run_test_case("Multiple contracts with gaps", test4_data, 12):
        passed_tests += 1
    
    # Test Case 5: Overlapping contracts (should be merged)
    test5_data = [
        {"isVacaciones": True, "fechaAlta": "01/01/2020", "fechaBaja": "15/01/2020"},  # 15 days vacation
        {"isVacaciones": False, "fechaAlta": "05/01/2020", "fechaBaja": "10/01/2020"},  # contract 1
        {"isVacaciones": False, "fechaAlta": "08/01/2020", "fechaBaja": "12/01/2020"}   # contract 2 (overlaps with 1)
    ]
    # Merged contract period: 05/01 to 12/01 = 8 days, non-overlapping: 15 - 8 = 7 days
    total_tests += 1
    if run_test_case("Overlapping contracts", test5_data, 7):
        passed_tests += 1
    
    # Test Case 6: Contract with no end date (active contract)
    test6_data = [
        {"isVacaciones": True, "fechaAlta": "01/01/2020", "fechaBaja": "05/01/2020"},  # 5 days vacation
        {"isVacaciones": False, "fechaAlta": "03/01/2020", "fechaBaja": ""}  # active contract from 3rd
    ]
    # Overlap from 03/01 to 05/01 = 3 days, non-overlapping: 5 - 3 = 2 days
    total_tests += 1
    if run_test_case("Active contract (no end date)", test6_data, 2):
        passed_tests += 1
    
    # Test Case 7: Single day vacation and contract
    test7_data = [
        {"isVacaciones": True, "fechaAlta": "01/01/2020", "fechaBaja": "01/01/2020"},  # 1 day vacation
        {"isVacaciones": True, "fechaAlta": "03/01/2020", "fechaBaja": "03/01/2020"},  # 1 day vacation
        {"isVacaciones": False, "fechaAlta": "01/01/2020", "fechaBaja": "01/01/2020"}  # 1 day contract (overlaps first)
    ]
    # First vacation overlaps completely (0 days), second vacation doesn't overlap (1 day)
    total_tests += 1
    if run_test_case("Single day periods", test7_data, 1):
        passed_tests += 1
    
    # Test Case 8: Invalid dates should be ignored
    test8_data = [
        {"isVacaciones": True, "fechaAlta": "01/01/2020", "fechaBaja": "03/01/2020"},  # 3 days vacation
        {"isVacaciones": True, "fechaAlta": "", "fechaBaja": "05/01/2020"},  # invalid vacation (ignored)
        {"isVacaciones": True, "fechaAlta": "invalid", "fechaBaja": "07/01/2020"},  # invalid vacation (ignored)
        {"isVacaciones": False, "fechaAlta": "10/01/2020", "fechaBaja": "15/01/2020"}  # contract (no overlap)
    ]
    total_tests += 1
    if run_test_case("Invalid dates", test8_data, 3):
        passed_tests += 1
    
    # Test Case 9: Vacation extends beyond contract end
    test9_data = [
        {"isVacaciones": True, "fechaAlta": "01/01/2020", "fechaBaja": "15/01/2020"},  # 15 days vacation
        {"isVacaciones": False, "fechaAlta": "05/01/2020", "fechaBaja": "10/01/2020"}  # 6 days contract
    ]
    # Overlap: 05/01 to 10/01 = 6 days, non-overlapping: 15 - 6 = 9 days
    total_tests += 1
    if run_test_case("Vacation extends beyond contract", test9_data, 9):
        passed_tests += 1
    
    # Test Case 10: Multiple vacations, some overlapping, some not
    test10_data = [
        {"isVacaciones": True, "fechaAlta": "01/01/2020", "fechaBaja": "05/01/2020"},  # 5 days vacation
        {"isVacaciones": True, "fechaAlta": "10/01/2020", "fechaBaja": "15/01/2020"},  # 6 days vacation
        {"isVacaciones": True, "fechaAlta": "20/01/2020", "fechaBaja": "25/01/2020"},  # 6 days vacation
        {"isVacaciones": False, "fechaAlta": "03/01/2020", "fechaBaja": "12/01/2020"}  # contract overlaps first two
    ]
    # First vacation: 5 days, overlap 3 days (03-05), non-overlap: 2 days
    # Second vacation: 6 days, overlap 3 days (10-12), non-overlap: 3 days  
    # Third vacation: 6 days, no overlap: 6 days
    # Total: 2 + 3 + 6 = 11 days
    total_tests += 1
    if run_test_case("Multiple vacations mixed overlaps", test10_data, 11):
        passed_tests += 1
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed_tests}/{total_tests} tests passed")
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
    else:
        print(f"❌ {total_tests - passed_tests} tests failed")
    print(f"{'='*50}")

if __name__ == "__main__":
    run_all_tests()