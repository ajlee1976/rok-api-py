# rok-api-py

A basic API wrapper for the online game [Rise of Kings Online](https://riseofkingsonline.com).

[API Documentation](https://wiki.riseofkingsonline.com/index.php/Mechanics/API)

Query a single Kingdom:
```py
kingdom = KingdomQuery(369).sync_request()

print(f"{kingdom.leader} is the leader of {kingdom.name}!")
```

Query all Kingdoms:
```py
all_kingdoms = KingdomsQuery().sync_request()

for kingdom in all_kingdoms:
    print(f"{kingdom.leader} is the leader of {kingdom.name}!")
```

Query Alliance:
```py
alliance = AllianceQuery().sync_request()

print(f"{alliance.name} has {alliance.score} score and {alliance.member_count} members!")
```