// SPDX-License-Identifier: MIT
pragma solidity ^0.8.34;

contract MedicalRecords {

    address public owner;

    mapping(uint256 => bytes32) private recordHashes;
    mapping(uint256 => bool) private recordExists;

    event RecordHashStored(
        uint256 indexed recordId,
        bytes32 recordHash,
        uint256 timestamp
    );

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can perform this action");
        _;
    }

    function storeRecordHash(
        uint256 recordId,
        bytes32 recordHash
    ) public onlyOwner {

        require(recordId > 0, "Invalid record ID");
        require(recordHash != bytes32(0), "Invalid record hash");
        require(!recordExists[recordId], "Record already exists");

        recordHashes[recordId] = recordHash;
        recordExists[recordId] = true;

        emit RecordHashStored(
            recordId,
            recordHash,
            block.timestamp
        );
    }

    function getRecordHash(
        uint256 recordId
    ) public view returns (bytes32) {

        require(recordExists[recordId], "Record does not exist");

        return recordHashes[recordId];
    }

    function verifyRecordHash(
        uint256 recordId,
        bytes32 candidateHash
    ) public view returns (bool) {

        if (!recordExists[recordId]) {
            return false;
        }

        return recordHashes[recordId] == candidateHash;
    }
}
