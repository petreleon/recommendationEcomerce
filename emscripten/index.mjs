import factory from './functions.js';

factory().then((instance) => {
  console.log(instance.rmse([1,1,1,1], [2,2,2,2])); // values can be returned, etc.
  console.log(instance.getEstimations([["133a","8a2"], ["1a","3a"]]));
  // instance.addRating("Veioza","Petre", 3);
  // instance.addRating("Veioza","Petre", 5);
  // instance.addRating("Veioza","Web", 2);
  // instance.deleteRating("Veioza","Web");
  console.log(instance.init(10000000));
  console.log(instance.mean());
});

// factory._sum_(1,2)