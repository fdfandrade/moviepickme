""" Fixtures used for testing """

def state_machine():
    ''' Basic state machine for testing '''
    simple_definition = (
        '{"Comment": "An example of the Amazon States Language using a choice state.",'
        '"StartAt": "DefaultState",'
        '"States": '
        '{"DefaultState": {"Type": "Fail","Error": "DefaultStateError","Cause": "No Matches!"}}}')
    return simple_definition
