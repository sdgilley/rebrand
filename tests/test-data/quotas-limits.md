---
title: Quotas and limits for Microsoft Foundry Agent Service
titleSuffix: Microsoft Foundry
description: Learn about the quotas and limits for when you use Microsoft Foundry Agent Service.
manager: nitinme
author: aahill
ms.author: aahi
ms.service: azure-ai-foundry
ms.subservice: azure-ai-foundry-agent-service
ms.topic: conceptual
ms.date: 07/03/2025
ms.custom: azure-ai-agents
monikerRange: 'foundry-classic || foundry'
---

# Microsoft Foundry Agent Service quotas and limits

This article contains a reference and a detailed description of the quotas and limits for Foundry Agent Service.

## Quotas and limits for the Foundry Agent Service

The following sections provide you with a guide to the default quotas and limits that apply to Foundry Agent Service:

| Limit Name | Limit Value |
|--|--|
| Maximum number of files per agent/thread | 10,000 |
| Maximum file size for agents | 512 MB |
| Maximum size for all uploaded files for agents | 300 GB |
| Maximum file size in tokens for attaching to a vector store | 2,000,000 tokens |
| Maximum number of messages per thread | 100,000 |
| Maximum size of `text` content per message | 1,500,000 characters |
| Maximum number of tools registered per agent | 128 |

## Quotas and limits for Azure OpenAI models

See the [Azure OpenAI](../openai/quotas-limits.md) for current quotas and limits for the Azure OpenAI models that you can use with Foundry Agent Service. 

## Next steps

[Learn about the models available for Foundry Agent Service](concepts\model-region-support.md)
