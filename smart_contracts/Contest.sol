// SPDX-License-Identifier: MIT
pragma solidity 0.8.0;

contract Contest{
	
	struct Contestant{
		uint id;
		string name;
		uint voteCount;
		string party;
		uint age;
		string qualification;
	}

	struct Voter{
		bool hasVoted;
		uint vote;
		bool isRegistered;
	}

	address admin;

	mapping(uint => Contestant) public contestants; 
	uint public contestantsCount;

	address[] public votersAddresses;
    mapping(address => Voter) public voters;

	enum PHASE{reg, voting , done}
	PHASE public state;


	modifier onlyAdmin(){
		require(msg.sender==admin, "must be an admin to perform this operation.");
		_;
	}
	
	modifier validState(PHASE x){
	    require(state==x, "must be a valid state(can't perform opertations in this phase)");
	    _;
	}

	constructor() {
		admin=msg.sender;
        state=PHASE.reg;
	}

    function changeState(PHASE x) onlyAdmin public{
		require(x > state, "must be a valid state(note: can't revert back to previous state)");
        state = x;
    }

	function addContestant(string memory _name , string memory _party , uint _age , string memory _qualification) public onlyAdmin validState(PHASE.reg){
		contestantsCount++;
		contestants[contestantsCount]=Contestant(contestantsCount,_name,0,_party,_age,_qualification);
	}

	function voterRegistration(address user) public onlyAdmin validState(PHASE.reg){
		votersAddresses.push(user);
		voters[user].isRegistered=true;
	}

	uint public votesCount;
	function vote(uint _contestantId) public validState(PHASE.voting){
        
		require(voters[msg.sender].isRegistered, "voter is not registered.");
		require(!voters[msg.sender].hasVoted, "voter has already voted.");
        require(_contestantId > 0 && _contestantId<=contestantsCount, "Invalid contestant ID (contestant ID must be > 0)");
		contestants[_contestantId].voteCount++;
		voters[msg.sender].hasVoted=true;
		voters[msg.sender].vote=_contestantId;
		votesCount++;
	}


	function votersCount() public view returns(uint) {
		return votersAddresses.length;
	}
	
	
}