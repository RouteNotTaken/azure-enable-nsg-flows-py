# azure_enable_nsg_flow_logs_py
Enabled Flow Logging on all NSGs in a given subscription. Python and Azure API
## Requirements
See requirements.txt
## Configuration
Define subscriptions and subscription IDs in config.yml.  
Storage Account is required for logs to write to, use Azure resource ID.
(Note: Storage Account must be in same region as the NSGs being configured)
## Examples
Configure Flows for all NSGs in the test subscription.  
`python3 ./enable_nsg_flows.py test`  
Configure Flows for all NSGs in the prod subscription.  
`python3 ./enable_nsg_flows.py prod`
## Sample Output
> ./enable_nsg_flows.py prod  
> app-prod-nsg: 202 Accepted  
> web-prod-nsg: 202 Accepted  
> db-prod-nsg: 202 Accepted  
