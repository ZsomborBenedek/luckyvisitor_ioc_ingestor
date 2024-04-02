# Lucky Visitor Scam IoC ingestor for Elasticsearch

Ingest Lucky Visitor scam IoCs into Elasticsearch:
- [Lucky Visitor IoC repository](https://github.com/JPCERTCC/Lucky-Visitor-Scam-IoC)

## Requirements

- `pip`
- `elasticsearch`
- SSH and Kibana access
- HTTP access to `github.com` on the backend

## Setup

- Clone the repository
- Make the setup script executable: `chmod +x setuplucky.sh`
- Run the script: `./setuplucky.sh`
- Enter the Elastic IP and API token and index for the logs (by default, `logs-ti_luckyvisitor`)

## How it works
- Runs each day at 11pm via cronjob  
- Pulls the day's indicator data from [https://github.com/JPCERTCC/Lucky-Visitor-Scam-IoC](https://github.com/JPCERTCC/Lucky-Visitor-Scam-IoC "https://github.com/jpcertcc/lucky-visitor-scam-ioc")  
- Transforms each indicator into JSON-objects  
- Sends it into the defined index with the LuckyVisitor-integration Elastic API key  
- If there were errors it writes into the `luckyvisitor_error.log` and `luckyvisitor_errors` dataset in Kibana

## Integrate error logs

- Integrations -> Custom Logs
- Set the dataset name to a custom one or leave it to generic

When the dataset is e.g. `luckyvisitor`, the data will use the `logs-luckyvisitor-*` index template/data view.

A custom ingest pipeline can also be created (e.g. `logs-luckyvisitor@custom`) which is displayed at the bottom:

```json
{
	"processors": [ 
		{ 
			"dissect": { 
				"field": "message", 
				"pattern": "%{@timestamp} - %{log.level} - %{message}" 
			}
		}, 
		{ 
			"date": {
				"field": "@timestamp", 
				"formats": [
					"ISO8601", 
					"yyyy-M-d H:m:s,q" 
				], 
				"timezone": "CET"
			}
		}
	]
}
```

Testing document for ingest pipeline:

```json
{
	"_source" : {
		"message" : "2024-02-19 15:49:00,172 - ERROR - test: *****"
	}
}
```
