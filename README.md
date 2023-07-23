# congenial-goggles (WIP)

A banking app that allows users to freely divide their financial goals into buckets and residences. 

## Buckets

Buckets are specific a measure of how much one wants to save towards a specific financial goal (i.e. Ryan's College Fund)

There can be one of two types of buckets, growing and static.

Static is a fixed amount one wants to save that does not change as you reach your goal (i.e. $5000 towards Ryan's College Fund)

Growing is a dynamic amount in which a user must contribute monthly towards their goal (i.e. $150 a month towards Vacation Savings)

## Residences

Residences are a large group in which buckets reside. For example; 'Ryan's College Fund' may reside within a larger residence called 'Children's College Funds', where you may have multiple funds for multiple children

## Instructions

PyInquirer is depended upon to help handle user input and menu navigation, and runs on Python version 3.9

Install required modules using requirements.txt

    pip install -r requirements.txt

## Examples

Main menu display

```
? Main Menu  (Use arrow keys)
 ❯ Status Menu
   Bucket Menu
   Residence Menu
   Exit
   Tutorial
```

Status menu where you can see the balance of a bucket and choose to add funds to it.

```
? Main Menu  Status Menu
? Status Menu  (Use arrow keys)
   Ryan's College Fund             
 ❯ Vacation Savings (Missing Funds)
   Return to Main Menu    
```

```
Bucket Vacation Savings has a balance of $0.00 and a monthly goal of $500.00. The last time you contributed was 2022-11-14.

? Would you like to add to Vacation Savings's balance?  (Use arrow keys)
 ❯ Yes
   No
   Return to Main Menu
```

```
? Would you like to add to Vacation Savings's balance?  Yes
? Contribute 500.00?  (Use arrow keys)
 ❯ Yes
   No
   Return to Main Menu
```

```
Successfully Added to Vacation Savings's Balance.
```

Bucket menu, where you can create, edit, or remove buckets.

```
? Main Menu  Bucket Menu
? Bucket Menu  (Use arrow keys)
 ❯ Create Bucket
   Edit Buckets
   Remove a Bucket
   Return to Main Menu
```

The Process of creating a bucket.

```
? Bucket Menu  Create Bucket
? New Bucket Name:  Example
? New Bucket Type:  Static
? New Bucket Target Goal:  1500
? New Bucket Residence:  Children's College Funds

New Bucket Example has been created.
```

You can also edit every setting of a bucket freely.

```
? Bucket Menu  Edit Buckets
? Choose a Bucket to Edit  Ryan's College Fund
? Choose a Setting to Edit  (Use arrow keys)
 ❯ Name: Ryan's College Fund
   Balance: $1000.00
   Type: Static
   Target Goal: $1000.00
   Residence: Children's College Funds
   Return to Main Menu
```

Deletion of a bucket.

```
? Bucket Menu  Remove a Bucket
? Choose a Bucket to Remove  (Use arrow keys)
   Ryan's College Fund
   Vacation Savings   
   Example            
 ❯ Return to Main Menu
```

```
? Bucket Menu  Remove a Bucket
? Choose a Bucket to Remove  Example
? Are you sure you wish to remove this bucket?  Yes
```

The residence menu. Very similar to the bucket menu, allowing for the same changes. Residences are far simpler however.

```
? Residence Menu  (Use arrow keys)
 ❯ Create Residence
   Edit Residences   
   Remove a Residence
   Return to Main Menu
```

The Tutorial, walking new users through how to use the program.

```
Congenial Goggles consists of buckets and residences.

Press Enter to Continue


Buckets represent your financial goals. How much you're trying to save and what you're saving it for.
How much you're saving can be either 'static' or 'growing'.

Press Enter to Continue


Static is a flat dollar amount to be saved.
Once the bucket is 'filled,' you no longer have to worry until you take some out.

Press Enter to Continue


Growing is a regular contribution to be made once per month.
The bucket 'grows' as you fill it.

Press Enter to Continue


Residences are where those buckets reside.
Whether that be a corresponding banking account (I.E. Chequeings Account),
or just a category (I.E. Children's College Fund)

Press Enter to Continue
```
