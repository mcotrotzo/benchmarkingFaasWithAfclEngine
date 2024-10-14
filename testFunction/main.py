import json
import requests
def test_function(event, context):
    request_json = request.get_json()
    print(request_json)

    language = request_json.get('language', '')
    input_file_characters = request_json.get('inputFileCharacters', 0)
    input_file_size = request_json.get('inputFileSize', 0)



    test_collection_of_int = request_json.get('testCollectionOfInt', [])
    test_collection_of_string = request_json.get('testCollectionOfString', [])
    test_collection_of_bool = request_json.get('testCollectionOfBool', [])






    result = testValueAndInput(input_file_size, input_file_characters, language,
                               test_collection_of_int, test_collection_of_string,
                               test_collection_of_bool)

    return json.dumps(result), 200
def testValueAndInput(input_file_size, input_file_characters, language, test_collection_of_int,
                      test_collection_of_string, test_collection_of_bool,
                      ):
    results = {}


    results['input_file_size'] = {
        'value': input_file_size,
        'is_valid': isinstance(input_file_size, (int, float)) and input_file_size >= 0
    }

    results['input_file_characters'] = {
        'value': input_file_characters,
        'is_valid': isinstance(input_file_characters, (int, float)) and input_file_characters >= 0
    }

    results['language'] = {
        'value': language,
        'is_valid': isinstance(language, str) and len(language) > 0
    }

    results['test_collection_of_int'] = {
        'value': test_collection_of_int,
        'is_valid': isinstance(test_collection_of_int, list) and all(isinstance(i, int) for i in test_collection_of_int)
    }

    results['test_collection_of_string'] = {
        'value': test_collection_of_string,
        'is_valid': isinstance(test_collection_of_string, list) and all(isinstance(i, str) for i in test_collection_of_string)
    }

    results['test_collection_of_bool'] = {
        'value': test_collection_of_bool,
        'is_valid': isinstance(test_collection_of_bool, list) and all(isinstance(i, bool) for i in test_collection_of_bool)
    }


    all_valid = all(res['is_valid'] for res in results.values())

    return {
        "succeed": all_valid,
        "details": results
    }
