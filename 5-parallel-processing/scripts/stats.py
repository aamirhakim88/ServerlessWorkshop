import boto3, time, json, sys, pickle
from datetime import datetime, timedelta
from tabulate import tabulate
from pprint import pprint

client = boto3.client('xray', region_name='ap-south-1')

def get_stats():
    trace_id = get_latest_trace()
    traces = client.batch_get_traces(TraceIds=[trace_id])
    print_stats(traces)

def print_stats(traces):
    worker_function_arn = get_worker_lambda_function()
    durations = []
    for _segment in traces[u'Traces'][0]['Segments']:
        segment = json.loads(_segment['Document'])
        subsegments = segment.get('subsegments', [])
        for subsegment in subsegments:
            if subsegment['name'] == 'parallel-call':
                durations.append(subsegment['end_time'] - subsegment['start_time'])
    print(tabulate([["Compute Time {}".format(durations.index(x) + 1), x] for x in durations]))
    if len(durations) is 0:
        print("No Initialization Time Found. Average Initialization Time = 0.00")
    else:
        print("Average Computation Time = {}".format(sum(durations)/len(durations)))
    print("Trace ID = {}".format(traces[u'Traces'][0]['Id']))

def get_latest_trace():
    # Set start time to one day before
    startTime = datetime.utcnow() - timedelta(hours = 1)
    endTime = datetime.utcnow()

    traces = []
    next_token = ''
    while next_token is not None:
        resp = client.get_trace_summaries(
            StartTime=startTime,
            EndTime=endTime,
            Sampling=False,
            NextToken=next_token
        )
        traces.extend(resp['TraceSummaries'])
        next_token = resp.get('NextToken', None)

    trace_data = []
    trace_ids = [t['Id'] for t in traces]

    time_info = []

    for trace_id in trace_ids:
        traces = client.batch_get_traces(TraceIds=[trace_id])        
        for trace in traces[u'Traces']:
            for _segment in trace['Segments']:
                segment = json.loads(_segment['Document'])
                if 'MasterLambda' in segment['name']:
                    time_info.append({'start_time': segment['start_time'], 'trace_id': segment['trace_id']})

    latest = max(time_info, key=lambda x: x['start_time'])
    return latest['trace_id']

def get_worker_lambda_function():
    cloudFormationClient = boto3.client('cloudformation', region_name='ap-south-1')
    stsClient = boto3.client('sts')

    stackResponse = cloudFormationClient.describe_stacks(
        StackName = "workshop-2018-deployment-" + stsClient.get_caller_identity()["Account"]
    )

    for output in stackResponse['Stacks'][0]['Outputs']:
        if output["OutputKey"] == "WorkerLambdaARN":
            return output["OutputValue"]


if __name__ == "__main__":
    get_stats()