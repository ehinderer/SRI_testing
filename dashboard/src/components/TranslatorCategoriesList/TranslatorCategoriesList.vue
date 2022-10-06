<template>
    <div>
        <span class="subheading">Subject categories</span><br>
        <v-chip-group>
        <v-chip small outlined v-for="subject_category in Object.entries(countBy(subject_categories))" v-bind:key="`${resource}_${subject_category}_all`">
            {{ formatCurie(subject_category[0]) }} ({{ subject_category[1] }})
        </v-chip>
        </v-chip-group>
        <span class="subheading">Object categories</span><br>
        <v-chip-group>
        <v-chip small outlined v-for="object_category in Object.entries(countBy(object_categories))" v-bind:key="`${resource}_${object_category}_all`">
            {{ formatCurie(object_category[0]) }} ({{ object_category[1] }})
        </v-chip>
        </v-chip-group>
        <span class="subheading">Predicates</span><br>
        <v-chip-group>
        <v-chip small outlined v-for="predicate in Object.entries(countBy(predicates))" v-bind:key="`${resource}_${predicate}_all`">
            {{ formatCurie(predicate[0]) }} ({{ predicate[1] }})
        </v-chip>
        </v-chip-group>
    </div>
</template>
<script>
import "lodash" as _

module export {
    name: "TranslatorCategoriesList",
    props: [
        "resource",
        "subject_categories",
        "object_categories",
        "predicates",
    ],
    methods: {
        formatCurie (curie) {
            return curie.split(':')[1];
        },
        countBy: _.countBy,
    }
}
</script>